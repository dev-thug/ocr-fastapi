from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
from .paddle_backend import PaddleBackend, _paddle_available
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class Box:
    points: List[Tuple[int, int]]
    text: str
    score: float


@dataclass
class RecognitionResult:
    text: str
    boxes: List[Box]


@dataclass
class StructureResult:
    tables: List[Dict[str, Any]]
    markdown: str | None = None


@dataclass
class ExtractionResult:
    entities: List[Dict[str, Any]]


class OcrEngine:
    def __init__(self, lang: str = "en", model: str = "pp-ocrv5") -> None:
        self.lang = lang
        self.model = model
        self._paddle: PaddleBackend | None = None
        if _paddle_available:
            try:
                self._paddle = PaddleBackend(lang=lang)
            except Exception:
                self._paddle = None

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.2, min=0.2, max=1))
    def recognize(self, content: bytes) -> RecognitionResult:
        if self._paddle is not None:
            try:
                text, boxes = self._paddle.recognize(content)
                return RecognitionResult(
                    text=text,
                    boxes=[Box(points=pts, text=txt, score=score) for pts, txt, score in boxes],
                )
            except Exception:
                # Graceful fallback on runtime errors
                return RecognitionResult(text="", boxes=[])
        # Fallback stub
        return RecognitionResult(text="stub", boxes=[])

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.2, min=0.2, max=1))
    def parse_structure(self, content: bytes) -> StructureResult:
        if self._paddle is not None:
            try:
                data = self._paddle.parse_structure(content)
                return StructureResult(tables=data.get("tables", []), markdown=data.get("markdown"))
            except Exception:
                return StructureResult(tables=[], markdown="")
        return StructureResult(tables=[], markdown="")

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=0.2, min=0.2, max=1))
    def extract_info(self, content: bytes) -> ExtractionResult:
        if self._paddle is not None:
            try:
                data = self._paddle.extract(content)
                return ExtractionResult(entities=data.get("entities", []))
            except Exception:
                return ExtractionResult(entities=[])
        return ExtractionResult(entities=[])
