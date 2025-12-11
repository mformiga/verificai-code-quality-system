"""
Vercel serverless function - ASGI handler
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables for Vercel
os.environ.setdefault('PYTHONPATH', os.path.dirname(__file__))

# Import and run FastAPI app
from app.main import app

# Vercel ASGI handler
from mangum import Mangum

# Create ASGI handler for Vercel
handler = Mangum(app)