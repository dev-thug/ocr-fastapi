"""
OCR Result Database Model

This module defines the SQLAlchemy model for storing OCR processing results.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class OCRResult(Base):
    """Database model for OCR processing results."""
    
    __tablename__ = "ocr_results"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_text = Column(Text, nullable=True)
    processed_text = Column(Text, nullable=True)
    confidence_score = Column(Integer, nullable=True)
    language = Column(String(10), nullable=False, default="eng")
    processing_time = Column(Integer, nullable=True)  # in milliseconds
    file_size = Column(Integer, nullable=True)  # in bytes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        """String representation of the OCR result."""
        return f"<OCRResult(id={self.id}, filename='{self.filename}', language='{self.language}')>"
    
    @property
    def processing_time_seconds(self) -> float:
        """Return processing time in seconds."""
        return self.processing_time / 1000.0 if self.processing_time else None
    
    @property
    def file_size_mb(self) -> float:
        """Return file size in megabytes."""
        return self.file_size / (1024 * 1024) if self.file_size else None 