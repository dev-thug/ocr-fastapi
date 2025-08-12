from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from app.core.config import settings
from app.core.logging import configure_logging
from app.api.schemas import StandardResponse, ok, fail
from app.api import errors as error_handlers
from app.ocr.engine import OcrEngine
from app.api.auth import require_auth
from app.middleware.request_id import RequestIdMiddleware
from app.routes.debug import router as debug_router
from PIL import Image
from io import BytesIO
import structlog
import subprocess
from typing import Any, List
import os


configure_logging()
log = structlog.get_logger()

app = FastAPI(title="OCR FastAPI Backend")
# Optional model preload on startup
@app.on_event("startup")
async def startup_preload():
    if settings.preload_models:
        # Determine languages to preload: PRELOAD_LANGS env (comma-separated) or default_lang
        raw_langs = os.getenv("PRELOAD_LANGS")
        if raw_langs:
            preload_langs = [part.strip() for part in raw_langs.split(",") if part.strip()]
        else:
            preload_langs = [settings.default_lang]

        for lang in dict.fromkeys(preload_langs):  # preserve order, dedupe
            try:
                log.info("preload_model", lang=lang, model=settings.model_default)
                OcrEngine(lang=lang, model=settings.model_default)
            except Exception:
                # best-effort preload; continue on errors
                log.warning("preload_failed", lang=lang, model=settings.model_default)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(RequestIdMiddleware)

# Minimal access log middleware
@app.middleware("http")
async def access_log(request, call_next):
    from time import perf_counter
    started = perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = int((perf_counter() - started) * 1000)
        log.bind(method=request.method, path=request.url.path, status=getattr(response, "status_code", 0), latency_ms=duration_ms)
        log.info("access")

# Routers
app.include_router(debug_router)

# Exception handlers
app.add_exception_handler(HTTPException, error_handlers.http_exception_handler)
app.add_exception_handler(Exception, error_handlers.unhandled_exception_handler)


@app.get("/health")
async def health():
    gpu: dict[str, Any] = {"visible": False}
    paddle_info: dict[str, Any] = {"version": None, "compiled_with_cuda": None}
    paddleocr_version: str | None = None
    # Collect Paddle/PaddleOCR versions dynamically if available
    try:
        import paddle  # type: ignore

        paddle_info["version"] = getattr(paddle, "__version__", None)
        try:
            paddle_info["compiled_with_cuda"] = bool(paddle.is_compiled_with_cuda())
        except Exception:
            paddle_info["compiled_with_cuda"] = None
    except Exception:
        paddle_info = {"version": None, "compiled_with_cuda": None}
    try:
        import paddleocr  # type: ignore

        paddleocr_version = getattr(paddleocr, "__version__", None)
    except Exception:
        paddleocr_version = None
    try:
        # Prefer NVML if available
        try:
            import pynvml  # type: ignore

            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu = {
                "visible": True,
                "utilization": int(util.gpu),
                "memory_used_mb": int(mem.used / (1024 * 1024)),
            }
            pynvml.nvmlShutdown()
        except Exception:
            out = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used",
                    "--format=csv,noheader,nounits",
                ],
                stderr=subprocess.STDOUT,
                timeout=1,
            ).decode().strip()
            if out:
                util, mem = out.split(",")
                gpu = {"visible": True, "utilization": int(util.strip()), "memory_used_mb": int(mem.strip())}
    except Exception:
        gpu = {"visible": False}
    return {
        "status": "ok",
        "gpu": gpu,
        "version": {"paddleocr": paddleocr_version, "paddlepaddle": paddle_info["version"], "compiled_with_cuda": paddle_info["compiled_with_cuda"]},
    }


@app.post("/ocr", response_model=StandardResponse, dependencies=[Depends(require_auth)])
async def ocr(file: UploadFile = File(...), lang: str = settings.default_lang, mode: str = "recognition", model: str = settings.model_default):
    # Normalize and validate language against allowed list
    lang = (lang or settings.default_lang).strip().lower()
    if settings.allowed_langs and lang not in settings.allowed_langs:
        return fail("BadRequest", "Unsupported language code", {"lang": lang, "allowed": settings.allowed_langs})
    # Guard by size if available (UploadFile.size may be undefined)
    try:
        size_attr = getattr(file, "size", None)
        if size_attr is not None and size_attr > settings.max_file_mb * 1024 * 1024:
            return fail("PayloadTooLarge", "File too large")
    except Exception:
        pass
    # Optional server-side image size guard
    buf = await file.read()
    if settings.max_image_px:
        try:
            im = Image.open(BytesIO(buf))
            w, h = im.size
            if max(w, h) > settings.max_image_px:
                im.thumbnail((settings.max_image_px, settings.max_image_px))
                out = BytesIO()
                im.save(out, format="PNG")
                buf = out.getvalue()
        except Exception:
            # If not an image, skip resizing and proceed (tests send text/plain)
            pass
    content = buf
    engine = OcrEngine(lang=lang, model=model)
    if mode == "recognition":
        res = engine.recognize(content)
        return ok({"text": res.text, "boxes": [
            {"box": b.points, "text": b.text, "score": b.score} for b in res.boxes
        ]}, meta={"lang": lang, "mode": mode, "model": model})
    if mode == "parsing":
        res = engine.parse_structure(content)
        return ok({"structure": {"tables": res.tables, "markdown": res.markdown}}, meta={"lang": lang, "mode": mode, "model": model})
    if mode == "extraction":
        res = engine.extract_info(content)
        return ok({"extraction": {"entities": res.entities}}, meta={"lang": lang, "mode": mode, "model": model})
    return fail("BadRequest", "Unsupported mode", {"mode": mode})


@app.post("/structure", response_model=StandardResponse, dependencies=[Depends(require_auth)])
async def structure(file: UploadFile = File(...), lang: str = settings.default_lang, model: str = settings.model_default):
    content = await file.read()
    engine = OcrEngine(lang=lang, model=model)
    res = engine.parse_structure(content)
    return ok({"structure": {"tables": res.tables, "markdown": res.markdown}})


@app.post("/extraction", response_model=StandardResponse, dependencies=[Depends(require_auth)])
async def extraction(file: UploadFile = File(...), lang: str = settings.default_lang, model: str = settings.model_default):
    content = await file.read()
    engine = OcrEngine(lang=lang, model=model)
    res = engine.extract_info(content)
    return ok({"extraction": {"entities": res.entities}})


# Batch processing endpoint to support 6.3 (batch option)
@app.post("/ocr/batch", response_model=StandardResponse, dependencies=[Depends(require_auth)])
async def ocr_batch(files: List[UploadFile] = File(...), lang: str = settings.default_lang, mode: str = "recognition", model: str = settings.model_default):
    engine = OcrEngine(lang=lang, model=model)
    results: list[dict[str, Any]] = []
    for f in files:
        try:
            buf = await f.read()
        except Exception:
            results.append({"error": "BadImage"})
            continue
        if mode == "recognition":
            r = engine.recognize(buf)
            results.append({"text": r.text, "boxes": [{"box": b.points, "text": b.text, "score": b.score} for b in r.boxes]})
        elif mode == "parsing":
            r = engine.parse_structure(buf)
            results.append({"structure": {"tables": r.tables, "markdown": r.markdown}})
        elif mode == "extraction":
            r = engine.extract_info(buf)
            results.append({"extraction": {"entities": r.entities}})
        else:
            results.append({"error": "BadRequest"})
    return ok({"items": results}, meta={"count": len(results), "mode": mode, "model": model})
