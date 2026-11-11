from pydantic import BaseModel
from typing import Optional


class RecipeCreate(BaseModel):
    name: str
    ingredient: Optional[str] = None
    dietary_tag: Optional[str] = None
    prep_time: Optional[int] = None


class RecipeResponse(RecipeCreate):
    id: int

    class Config:
        from_attributes = True
