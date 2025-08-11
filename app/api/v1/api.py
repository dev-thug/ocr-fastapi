"""
API v1 Router

This module contains the main API v1 router that includes all endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import ocr

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"]) 