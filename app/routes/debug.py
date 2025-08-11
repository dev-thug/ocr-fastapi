from __future__ import annotations
from fastapi import APIRouter, Depends
from app.api.auth import require_auth

router = APIRouter(prefix="/debug", tags=["debug"], dependencies=[Depends(require_auth)])


@router.get("/paddle")
async def paddle_status():
    status = {"available": False, "compiled_with_cuda": None, "run_check": None, "version": None}
    try:
        import paddle  # type: ignore

        status["available"] = True
        status["version"] = getattr(paddle, "__version__", None)
        try:
            status["compiled_with_cuda"] = bool(paddle.is_compiled_with_cuda())
        except Exception:
            status["compiled_with_cuda"] = None
        try:
            from paddle.utils.run_check import run_check  # type: ignore

            run_check()
            status["run_check"] = True
        except Exception:
            status["run_check"] = False
    except Exception:
        pass
    return status
