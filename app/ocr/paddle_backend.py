from __future__ import annotations
from typing import Any, List, Tuple
import os
from io import BytesIO
from PIL import Image
import numpy as np

try:
    from paddleocr import PaddleOCR  # type: ignore
    _paddle_available = True
except Exception:  # pragma: no cover
    PaddleOCR = None  # type: ignore
    _paddle_available = False

try:
    # PP-Structure entrypoint (if packaged)
    from paddleocr import PPStructure  # type: ignore
    _pp_structure_available = True
except Exception:  # pragma: no cover
    PPStructure = None  # type: ignore
    _pp_structure_available = False


class PaddleBackend:
    def __init__(self, lang: str = "en", use_gpu: bool | None = None) -> None:
        if not _paddle_available:
            raise RuntimeError("PaddleOCR not available")
        # Resolve GPU usage: env > explicit arg > auto-detect
        resolved_use_gpu: bool | None = use_gpu
        env_flag = os.getenv("PADDLE_USE_GPU")
        if env_flag is not None:
            if env_flag.strip().lower() in ("1", "true", "yes", "on"):  # force enable
                resolved_use_gpu = True
            elif env_flag.strip().lower() in ("0", "false", "no", "off"):  # force disable
                resolved_use_gpu = False
        if resolved_use_gpu is None:
            try:
                import paddle  # type: ignore

                if getattr(paddle, "is_compiled_with_cuda", lambda: False)():
                    try:
                        paddle.device.set_device("gpu")  # ensure GPU context
                    except Exception:
                        pass
                    resolved_use_gpu = True
                else:
                    resolved_use_gpu = False
            except Exception:
                resolved_use_gpu = False

        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=resolved_use_gpu)
        # Lazily create PP-Structure only when needed to avoid SystemExit on unsupported langs
        self._pp_structure = None

    def _decode(self, content: bytes) -> Any:
        img = Image.open(BytesIO(content)).convert("RGB")
        return np.array(img)

    def recognize(self, image: Any | bytes) -> tuple[str, list[tuple[list[tuple[int, int]], str, float]]]:
        if isinstance(image, (bytes, bytearray)):
            image = self._decode(image)
        result = self.ocr.ocr(image, cls=True)
        text_all: List[str] = []
        boxes_all: list[tuple[list[tuple[int, int]], str, float]] = []
        for line in result[0]:
            box_points = [(int(x), int(y)) for x, y in line[0]]
            txt = line[1][0]
            score = float(line[1][1])
            text_all.append(txt)
            boxes_all.append((box_points, txt, score))
        return (" ".join(text_all), boxes_all)

    def parse_structure(self, image: Any | bytes) -> dict:
        if isinstance(image, (bytes, bytearray)):
            image = self._decode(image)
        # Lazy init PP-Structure here
        if self._pp_structure is None and _pp_structure_available:
            try:
                self._pp_structure = PPStructure(layout=True, table=True, ocr=True, lang=self.ocr.lang)  # type: ignore
            except BaseException:
                # Catch SystemExit raised internally by PP-Structure on unsupported languages
                self._pp_structure = None
        if self._pp_structure is not None:
            try:
                elements = self._pp_structure(image)  # type: ignore
                tables: list[dict] = []
                md_lines: list[str] = []
                for el in elements:
                    typ = el.get("type")
                    if typ == "table":
                        tables.append({"bbox": el.get("bbox"), "html": el.get("res")})
                    elif typ in ("text", "title", "paragraph"):
                        md_lines.append(str(el.get("res")))
                return {"tables": tables, "markdown": "\n".join(md_lines)}
            except Exception:
                # If runtime error, fall back below
                pass
        # Fallback to OCR text as markdown-like output
        text, _ = self.recognize(image)
        return {"tables": [], "markdown": text}

    def extract(self, image: Any | bytes) -> dict:
        if isinstance(image, (bytes, bytearray)):
            image = self._decode(image)
        # Placeholder: ChatOCRv4/ERNIE PoC hook — gated by settings
        try:
            from app.core.config import settings  # lazy import to avoid cycles
            if getattr(settings, "chatocr_enabled", False) and settings.chatocr_api_token:
                # PoC: enrich with a dummy entity indicating ChatOCR path used
                text, _ = self.recognize(image)
                return {"entities": [{"text": text, "type": "chatocr_poc"}]}
        except Exception:
            pass
        # Default fallback
        text, _ = self.recognize(image)
        return {"entities": [{"text": text, "type": "summary"}]}
