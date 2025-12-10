"""
Vercel serverless function entry point for the backend API
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the FastAPI app
from app.main import app

# Vercel will use the app directly
handler = app