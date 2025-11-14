#!/usr/bin/env python3
"""
Debug script to check FastAPI router registration
"""

import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.main import app

def print_routes():
    """Print all registered routes"""
    print("FastAPI Routes:")
    print("=" * 50)

    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"{list(route.methods)} {route.path}")
        elif hasattr(route, 'path'):
            print(f"[Static] {route.path}")
        else:
            print(f"[Other] {route}")

if __name__ == "__main__":
    print_routes()