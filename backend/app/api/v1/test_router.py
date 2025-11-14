"""
Test router for PUT methods
"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.put("/test-put")
async def test_put():
    """Simple test PUT endpoint"""
    return {"message": "PUT test successful", "method": "PUT"}


@router.post("/test-post")
async def test_post():
    """Simple test POST endpoint"""
    return {"message": "POST test successful", "method": "POST"}


@router.get("/test-get")
async def test_get():
    """Simple test GET endpoint"""
    return {"message": "GET test successful", "method": "GET"}