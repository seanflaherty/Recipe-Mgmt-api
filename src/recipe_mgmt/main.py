"""Main application module for the Recipe Management API.

This module initializes the FastAPI application and defines core HTTP
request handler functions (`get_recipes`, `add_recipe`, and `delete_recipe`),
managing in-memory state and disk persistence (`storage.py`).
"""

from pathlib import Path
from typing import List, Optional
import json
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from .database import get_db, engine, Base
from .models import RecipeModel, RecipeIngredientModel, InstructionModel

# Automatically create tables for SQLite/Postgres on startup.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recipe Management API",
    version="1.0.0",
    docs_url="/ui",  # Keeps the UI path.
    redoc_url=None,
)

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"

# Mount the static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --- Pydantic Models for Request Validation & Swagger UI ---
class IngredientSchema(BaseModel):
    name: str = Field(..., example="Flour")
    dietary_tags: List[str] = Field(default=[], example=["VEGAN", "GLUTEN"])


class RecipeIngredientSchema(BaseModel):
    ingredient: IngredientSchema
    quantity: float = Field(default=1.0, example=2.0)
    unit: str = Field(default="", example="cups")


class InstructionSchema(BaseModel):
    description: str = Field(..., example="Mix ingredients in a bowl.")
    equipment: List[str] = Field(default=[], example=["mixing bowl", "spoon"])
    prep_time: int = Field(default=0, example=5)
    include_in_prep_time: bool = Field(default=True)


class RecipeCreateSchema(BaseModel):
    name: str = Field(..., example="Homemade Bread")
    recipe_ingredients: List[RecipeIngredientSchema] = []
    instructions: List[InstructionSchema] = []


@app.get("/")
async def read_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/recipes-db", summary="Get recipes from database")
def get_db_recipes(
    name: Optional[str] = Query(
        None, description="Filter by recipe name (partial match)"
    ),
    db: Session = Depends(get_db),
):
    """Fetch all recipes from the database and return formatted HTML links containing recipe JSON data."""
    query = db.query(RecipeModel)
    if name:
        query = query.filter(RecipeModel.name.ilike(f"%{name}%"))

    recipes = query.all()

    if not recipes:
        return "<p class='text-gray-400 italic text-sm'>No recipes found in the database.</p>"

    html_output = "<ul class='divide-y divide-gray-100 space-y-2'>"
    for r in recipes:
        total_prep = sum(
            ins.prep_time for ins in r.instructions if ins.include_in_prep_time
        )

        # Build dictionary containing all recipe fields
        recipe_dict = {
            "name": r.name,
            "total_prep_time": total_prep,
            "ingredients": [
                {
                    "name": ing.ingredient_name,
                    "quantity": ing.quantity,
                    "unit": ing.unit,
                    "dietary_tags": (
                        ing.dietary_tags.split(",") if ing.dietary_tags else []
                    ),
                }
                for ing in r.ingredients
            ],
            "instructions": [
                {
                    "description": ins.description,
                    "equipment": ins.equipment.split(",") if ins.equipment else [],
                    "prep_time": ins.prep_time,
                    "include_in_prep_time": ins.include_in_prep_time,
                }
                for ins in r.instructions
            ],
        }

        # Convert dictionary to a compact JSON string
        recipe_json = json.dumps(recipe_dict)

        html_output += f"""
        <li class='py-2 flex justify-between items-center'>
            <button onclick='openRecipeModal(this)'
                    data-recipe='{recipe_json}'
                    class='text-emerald-600 font-medium hover:text-emerald-800 hover:underline text-left text-sm transition'>
                🍳 {r.name}
            </button>
            <span class='text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-full'>⏱️ {total_prep} mins</span>
        </li>
        """
    html_output += "</ul>"

    return HTMLResponse(content=html_output)


@app.post("/recipes", status_code=201, summary="Add a recipe to the database")
def add_recipe(recipe_data: RecipeCreateSchema, db: Session = Depends(get_db)):
    """Add a new recipe to the database and optionally keep CSV persistence."""
    try:
        # Check if a recipe with this name already exists
        existing_recipe = (
            db.query(RecipeModel).filter(RecipeModel.name == recipe_data.name).first()
        )
        if existing_recipe:
            raise HTTPException(
                status_code=400,
                detail=f"Recipe '{recipe_data.name}' already exists in the database.",
            )

        # Create the main Recipe database record
        db_recipe = RecipeModel(name=recipe_data.name)

        # Add ingredients
        for ri in recipe_data.recipe_ingredients:
            tags_str = ",".join(ri.ingredient.dietary_tags)
            db_ingredient = RecipeIngredientModel(
                ingredient_name=ri.ingredient.name,
                quantity=ri.quantity,
                unit=ri.unit,
                dietary_tags=tags_str,
            )
            db_recipe.ingredients.append(db_ingredient)

        # Add instructions
        for ins in recipe_data.instructions:
            equipment_str = ",".join(ins.equipment)
            db_instruction = InstructionModel(
                description=ins.description,
                equipment=equipment_str,
                prep_time=ins.prep_time,
                include_in_prep_time=ins.include_in_prep_time,
            )
            db_recipe.instructions.append(db_instruction)

        # Commit to database (SQLite or PostgreSQL)
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)

        return {
            "message": "Recipe added and saved to database successfully!",
            "id": db_recipe.id,
            "name": db_recipe.name,
            "ingredient_count": len(db_recipe.ingredients),
            "instruction_count": len(db_recipe.instructions),
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/recipes/{name}", summary="Delete a recipe by name")
def delete_recipe(name: str, db: Session = Depends(get_db)):
    """Remove a recipe by name from the database."""
    db_recipe = db.query(RecipeModel).filter(RecipeModel.name == name).first()
    if not db_recipe:
        raise HTTPException(
            status_code=404,
            detail=f"Recipe '{name}' not found in the database.",
        )

    try:
        db.delete(db_recipe)
        db.commit()
        return {"message": f"Recipe '{name}' deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Mount the "static" folder to the root URL
app.mount("/", StaticFiles(directory="static", html=True), name="static")
