"""Pydantic data validation and serialization schemas for the API.

This module defines data transfer objects (DTOs) using Pydantic models
to validate incoming request payloads and serialize outgoing response objects
for recipe management operations.
"""

from typing import Optional
from pydantic import BaseModel


class RecipeCreate(BaseModel):
    """Pydantic validation schema for creating a new recipe.

    Attributes:
        name: The display name of the recipe.
        ingredient: An optional single ingredient string.
        dietary_tag: An optional dietary restriction or tag.
        prep_time: The estimated preparation time in minutes.
    """

    name: str
    ingredient: Optional[str] = None
    dietary_tag: Optional[str] = None
    prep_time: Optional[int] = None


class RecipeResponse(RecipeCreate):
    """Pydantic serialization schema for returning a recipe record with its ID.

    Attributes:
        id: The unique primary key identifier of the recipe in the database[cite: 2].
        name: The display name of the recipe[cite: 2].
        ingredient: An optional single ingredient string[cite: 2].
        dietary_tag: An optional dietary restriction or tag[cite: 2].
        prep_time: The estimated preparation time in minutes[cite: 2].
    """

    id: int

    class Config:
        """Pydantic model configuration settings."""

        from_attributes = True
