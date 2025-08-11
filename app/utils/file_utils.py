"""
File Utility Functions

This module contains utility functions for file handling, validation,
and upload directory management.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile

from app.core.config import settings


def validate_file_extension(filename: str) -> bool:
    """
    Validate if file extension is allowed.
    
    Args:
        filename: Name of the file to validate
        
    Returns:
        bool: True if extension is allowed, False otherwise
    """
    file_ext = Path(filename).suffix.lower()
    return file_ext in settings.ALLOWED_EXTENSIONS


def validate_file_size(file_size: int) -> bool:
    """
    Validate if file size is within limits.
    
    Args:
        file_size: Size of the file in bytes
        
    Returns:
        bool: True if size is within limits, False otherwise
    """
    return file_size <= settings.MAX_FILE_SIZE


def create_upload_directory() -> Path:
    """
    Create upload directory if it doesn't exist.
    
    Returns:
        Path: Path to the upload directory
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    return upload_dir


def save_upload_file(upload_file: UploadFile, filename: Optional[str] = None) -> str:
    """
    Save uploaded file to disk.
    
    Args:
        upload_file: FastAPI UploadFile object
        filename: Optional custom filename
        
    Returns:
        str: Path to the saved file
        
    Raises:
        HTTPException: If file validation fails
    """
    # Validate file extension
    if not validate_file_extension(upload_file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File extension not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Create upload directory
    upload_dir = create_upload_directory()
    
    # Generate filename if not provided
    if filename is None:
        filename = upload_file.filename
    
    # Create unique filename to avoid conflicts
    file_path = upload_dir / filename
    counter = 1
    while file_path.exists():
        name, ext = os.path.splitext(filename)
        file_path = upload_dir / f"{name}_{counter}{ext}"
        counter += 1
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    
    return str(file_path)


def delete_file(file_path: str) -> bool:
    """
    Delete file from disk.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        bool: True if file was deleted, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_info(file_path: str) -> dict:
    """
    Get file information.
    
    Args:
        file_path: Path to the file
        
    Returns:
        dict: File information including size, extension, etc.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    stat = path.stat()
    return {
        "filename": path.name,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "extension": path.suffix.lower(),
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
    }


def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """
    Clean up old files from directory.
    
    Args:
        directory: Directory to clean up
        max_age_hours: Maximum age of files in hours
        
    Returns:
        int: Number of files deleted
    """
    import time
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    if delete_file(file_path):
                        deleted_count += 1
    except Exception:
        pass
    
    return deleted_count 