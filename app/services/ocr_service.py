"""
PaddleOCR Service

This module contains the OCR processing service that handles image text extraction
using PaddleOCR 3.1 engine.
"""

import os
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

import cv2
import numpy as np
from PIL import Image
import paddle
from paddleocr import PaddleOCR

from app.core.config import settings
from app.models.ocr_result import OCRResult
from app.schemas.ocr import OCRRequest


class PaddleOCRService:
    """Service class for PaddleOCR processing operations."""
    
    def __init__(self):
        """Initialize PaddleOCR service with configuration."""
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.default_language = settings.DEFAULT_LANGUAGE
        
        # Set GPU device if available (Paddle 3.1 way)
        try:
            paddle.device.set_device('gpu')
            self.use_gpu = True
        except:
            paddle.device.set_device('cpu')
            self.use_gpu = False
        
        # Initialize PaddleOCR with configuration
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=self.default_language,
            use_gpu=self.use_gpu,
            use_mp=True,
            total_process_num=1,
            enable_mkldnn=True,
            cpu_threads=10,
            use_tensorrt=False,
            use_fp16=False,
            det_db_thresh=0.3,
            det_db_box_thresh=0.6,
            det_db_unclip_ratio=1.6,
            use_zero_copy_run=False,
            use_pdf2docx_api=False,
            use_space_char=True,
            drop_score=0.5,
            det_limit_side_num=960,
            det_limit_type='max',
            rec_batch_num=6,
            use_greedy_decoder=False,
            ocr_version='PP-OCRv5'  # Use latest version
        )
    
    def validate_language(self, language: str) -> str:
        """
        Validate and return the language code.
        
        Args:
            language: Language code to validate
            
        Returns:
            str: Validated language code
            
        Raises:
            ValueError: If language is not supported
        """
        if language not in self.supported_languages:
            raise ValueError(f"Language '{language}' not supported. Supported languages: {self.supported_languages}")
        return language
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            np.ndarray: Preprocessed image
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Basic preprocessing
        # Resize if too large
        height, width = image_rgb.shape[:2]
        max_size = 2048
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image_rgb = cv2.resize(image_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Enhance contrast
        lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    def extract_text(self, image_path: str, language: str = None, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Extract text from image using PaddleOCR.
        
        Args:
            image_path: Path to the image file
            language: Language code for OCR processing
            confidence_threshold: Minimum confidence threshold for text detection
            
        Returns:
            Dict[str, Any]: OCR results with text, confidence scores, and metadata
        """
        start_time = time.time()
        
        # Validate language
        if language is None:
            language = self.default_language
        language = self.validate_language(language)
        
        # Update OCR language if different
        if language != self.ocr.lang:
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang=language,
                use_gpu=self.use_gpu,
                use_mp=True,
                total_process_num=1,
                enable_mkldnn=True,
                cpu_threads=10,
                use_tensorrt=False,
                use_fp16=False,
                det_db_thresh=0.3,
                det_db_box_thresh=0.6,
                det_db_unclip_ratio=1.6,
                max_batch_size=10,
                use_zero_copy_run=False,
                use_pdf2docx_api=False,
                use_space_char=True,
                drop_score=confidence_threshold,
                det_limit_side_num=960,
                det_limit_type='max',
                rec_batch_num=6,
                use_greedy_decoder=False,
                ocr_version='PP-OCRv5'
            )
        
        # Preprocess image
        processed_image = self.preprocess_image(image_path)
        
        # Perform OCR
        try:
            results = self.ocr.ocr(processed_image, cls=True)
            
            # Process results
            extracted_texts = []
            total_confidence = 0.0
            text_count = 0
            
            if results and results[0]:
                for line in results[0]:
                    if line and len(line) >= 2:
                        text_info = line[1]
                        if len(text_info) >= 2:
                            text = text_info[0]
                            confidence = text_info[1]
                            
                            if confidence >= confidence_threshold:
                                extracted_texts.append({
                                    'text': text,
                                    'confidence': confidence,
                                    'bbox': line[0] if line[0] else None
                                })
                                total_confidence += confidence
                                text_count += 1
            
            # Calculate average confidence
            avg_confidence = (total_confidence / text_count * 100) if text_count > 0 else 0.0
            
            # Combine all text
            full_text = ' '.join([item['text'] for item in extracted_texts])
            
            processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            return {
                'original_text': full_text,
                'processed_text': full_text,
                'confidence_score': int(avg_confidence),
                'processing_time': processing_time,
                'language': language,
                'text_blocks': extracted_texts,
                'total_blocks': text_count,
                'gpu_used': self.use_gpu
            }
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return {
                'original_text': '',
                'processed_text': '',
                'confidence_score': 0,
                'processing_time': processing_time,
                'language': language,
                'error': str(e),
                'text_blocks': [],
                'total_blocks': 0,
                'gpu_used': self.use_gpu
            }
    
    def save_ocr_result(self, db_session, filename: str, ocr_result: Dict[str, Any]) -> OCRResult:
        """
        Save OCR result to database.
        
        Args:
            db_session: Database session
            filename: Original filename
            ocr_result: OCR processing results
            
        Returns:
            OCRResult: Saved OCR result object
        """
        # Get file size
        file_path = Path(settings.UPLOAD_DIR) / filename
        file_size = file_path.stat().st_size if file_path.exists() else 0
        
        # Create OCR result object
        ocr_result_obj = OCRResult(
            filename=filename,
            original_text=ocr_result.get('original_text', ''),
            processed_text=ocr_result.get('processed_text', ''),
            confidence_score=ocr_result.get('confidence_score', 0),
            language=ocr_result.get('language', self.default_language),
            processing_time=ocr_result.get('processing_time', 0),
            file_size=file_size
        )
        
        # Save to database
        db_session.add(ocr_result_obj)
        db_session.commit()
        db_session.refresh(ocr_result_obj)
        
        return ocr_result_obj
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information for PaddleOCR.
        
        Returns:
            Dict[str, Any]: System information
        """
        return {
            'paddle_version': paddle.__version__,
            'gpu_available': self.use_gpu,
            'supported_languages': self.supported_languages,
            'default_language': self.default_language,
            'ocr_version': 'PP-OCRv5'
        }


# Create service instance
ocr_service = PaddleOCRService() 