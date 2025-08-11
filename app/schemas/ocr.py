"""
OCR Pydantic Schemas

This module defines Pydantic models for OCR request/response validation.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class OCRRequest(BaseModel):
    """Schema for OCR processing request."""
    
    language: str = Field(
        default="korean",
        description="Language code for OCR processing (e.g., 'korean', 'en', 'ch')",
        example="korean"
    )
    confidence_threshold: Optional[float] = Field(
        default=0.5,
        description="Minimum confidence threshold for text detection (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.5
    )
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "language": "korean",
                "confidence_threshold": 0.5
            }
        }


class OCRResponse(BaseModel):
    """Schema for OCR processing response."""
    
    id: int = Field(..., description="OCR result ID")
    filename: str = Field(..., description="Original filename")
    original_text: str = Field(..., description="Extracted text from image")
    processed_text: str = Field(..., description="Processed text (same as original for now)")
    confidence_score: int = Field(..., description="Average confidence score (0-100)")
    language: str = Field(..., description="Language used for OCR processing")
    processing_time: int = Field(..., description="Processing time in milliseconds")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    created_at: datetime = Field(..., description="Timestamp when result was created")
    status: str = Field(..., description="Processing status")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "filename": "sample.jpg",
                "original_text": "안녕하세요",
                "processed_text": "안녕하세요",
                "confidence_score": 85,
                "language": "korean",
                "processing_time": 1200,
                "file_size": 1024000,
                "created_at": "2024-01-01T12:00:00Z",
                "status": "success"
            }
        }


class OCRResultList(BaseModel):
    """Schema for paginated OCR results list."""
    
    items: List[OCRResponse] = Field(..., description="List of OCR results")
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "size": 10,
                "pages": 0
            }
        }


class OCRStatus(BaseModel):
    """Schema for OCR service status."""
    
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="OCR service name")
    version: str = Field(..., description="Service version")
    supported_languages: List[str] = Field(..., description="List of supported languages")
    paddle_version: Optional[str] = Field(None, description="PaddlePaddle version")
    gpu_available: Optional[bool] = Field(None, description="GPU availability")
    ocr_version: Optional[str] = Field(None, description="OCR model version")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "status": "healthy",
                "service": "PaddleOCR",
                "version": "3.1.0",
                "supported_languages": ["korean", "en", "ch"],
                "paddle_version": "2.6.2",
                "gpu_available": True,
                "ocr_version": "PP-OCRv5"
            }
        } 