"""
OCR API Endpoints

This module contains the OCR-related API endpoints for image processing
and text extraction using PaddleOCR 3.1.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.ocr_result import OCRResult
from app.schemas.ocr import OCRRequest, OCRResponse, OCRResultList, OCRStatus
from app.services.ocr_service import ocr_service
from app.utils.file_utils import save_upload_file, delete_file

router = APIRouter()


@router.post("/upload", response_model=OCRResponse)
async def upload_and_process_image(
    file: UploadFile = File(...),
    language: str = Form("korean"),
    confidence_threshold: Optional[float] = Form(0.5),
    db: Session = Depends(get_db)
):
    """
    Upload and process image for OCR text extraction using PaddleOCR 3.1.
    
    Args:
        file: Image file to process
        language: Language code for OCR processing (default: korean)
        confidence_threshold: Minimum confidence threshold (0.0-1.0)
        db: Database session
        
    Returns:
        OCRResponse: OCR processing results
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Save uploaded file
        file_path = save_upload_file(file)
        
        try:
            # Process image with PaddleOCR
            ocr_result = ocr_service.extract_text(
                image_path=file_path,
                language=language,
                confidence_threshold=confidence_threshold
            )
            
            # Save result to database
            db_result = ocr_service.save_ocr_result(
                db_session=db,
                filename=file.filename,
                ocr_result=ocr_result
            )
            
            # Clean up uploaded file
            delete_file(file_path)
            
            return OCRResponse(
                id=db_result.id,
                filename=db_result.filename,
                original_text=db_result.original_text,
                processed_text=db_result.processed_text,
                confidence_score=db_result.confidence_score,
                language=db_result.language,
                processing_time=db_result.processing_time,
                file_size=db_result.file_size,
                created_at=db_result.created_at,
                status="success"
            )
            
        except Exception as e:
            # Clean up uploaded file on error
            delete_file(file_path)
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/results", response_model=OCRResultList)
async def get_ocr_results(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    language: Optional[str] = Query(None, description="Filter by language"),
    min_confidence: Optional[int] = Query(None, ge=0, le=100, description="Minimum confidence score"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of OCR results with optional filtering.
    
    Args:
        page: Page number (1-based)
        size: Number of items per page
        language: Filter by language code
        min_confidence: Filter by minimum confidence score
        db: Database session
        
    Returns:
        OCRResultList: Paginated OCR results
    """
    try:
        # Build query
        query = db.query(OCRResult)
        
        # Apply filters
        if language:
            query = query.filter(OCRResult.language == language)
        if min_confidence is not None:
            query = query.filter(OCRResult.confidence_score >= min_confidence)
        
        # Apply ordering
        query = query.order_by(OCRResult.created_at.desc())
        
        # Apply pagination
        total = query.count()
        results = query.offset((page - 1) * size).limit(size).all()
        
        # Convert to response models
        ocr_results = [
            OCRResponse(
                id=result.id,
                filename=result.filename,
                original_text=result.original_text,
                processed_text=result.processed_text,
                confidence_score=result.confidence_score,
                language=result.language,
                processing_time=result.processing_time,
                file_size=result.file_size,
                created_at=result.created_at,
                status="success"
            )
            for result in results
        ]
        
        return OCRResultList(
            items=ocr_results,
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")


@router.get("/results/{result_id}", response_model=OCRResponse)
async def get_ocr_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific OCR result by ID.
    
    Args:
        result_id: OCR result ID
        db: Database session
        
    Returns:
        OCRResponse: OCR result details
    """
    try:
        result = db.query(OCRResult).filter(OCRResult.id == result_id).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="OCR result not found")
        
        return OCRResponse(
            id=result.id,
            filename=result.filename,
            original_text=result.original_text,
            processed_text=result.processed_text,
            confidence_score=result.confidence_score,
            language=result.language,
            processing_time=result.processing_time,
            file_size=result.file_size,
            created_at=result.created_at,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve result: {str(e)}")


@router.delete("/results/{result_id}")
async def delete_ocr_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete OCR result by ID.
    
    Args:
        result_id: OCR result ID
        db: Database session
        
    Returns:
        dict: Success message
    """
    try:
        result = db.query(OCRResult).filter(OCRResult.id == result_id).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="OCR result not found")
        
        # Delete from database
        db.delete(result)
        db.commit()
        
        return {"message": "OCR result deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete result: {str(e)}")


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages for OCR processing.
    
    Returns:
        dict: Supported languages information
    """
    return {
        "supported_languages": ocr_service.supported_languages,
        "default_language": ocr_service.default_language
    }


@router.get("/health", response_model=OCRStatus)
async def health_check():
    """
    Health check endpoint for OCR service.
    
    Returns:
        OCRStatus: Service status information
    """
    system_info = ocr_service.get_system_info()
    return OCRStatus(
        status="healthy",
        service="PaddleOCR",
        version="3.1.0",
        supported_languages=ocr_service.supported_languages,
        paddle_version=system_info.get('paddle_version'),
        gpu_available=system_info.get('gpu_available'),
        ocr_version=system_info.get('ocr_version')
    )


@router.get("/system-info")
async def get_system_info():
    """
    Get detailed system information for PaddleOCR.
    
    Returns:
        dict: Detailed system information
    """
    return ocr_service.get_system_info() 