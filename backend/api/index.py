"""
Vercel serverless function entry point
"""
import os
import sys

# Set environment
os.environ.setdefault("PYTHONPATH", "/var/task")

# Simple response for testing
def handler(request):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        },
        "body": '{"message": "Backend is working", "status": "ok"}'
    }