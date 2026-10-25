"""Tests for the Recipe Management app/api"""
from app import create_app


def test_can_create_app():
    """Basic sanity check test."""
    app = create_app()
    assert app is not None