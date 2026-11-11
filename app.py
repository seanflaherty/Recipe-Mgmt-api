"""
Recipe Management Application Entry Point.

This module initializes and configures the FastAPI application instance,
setting up sys.path adjustments and exposing the core ASGI application
interface for production servers.
"""

import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, "src"))

# Import the FastAPI app instance from the main module
from recipe_mgmt.main import app


@app.get("/")
def home():
    """Root health check endpoint."""
    return {"message": "Hello recipes! (root)"}
