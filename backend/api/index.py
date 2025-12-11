"""
Vercel serverless function entry point for the backend API
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Import the FastAPI app
from app.main import app

# Export the app for Vercel
handler = app