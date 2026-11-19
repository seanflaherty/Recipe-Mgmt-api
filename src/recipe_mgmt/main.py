"""FastAPI application entry point for the Recipe Management API.

This module initializes the FastAPI application, mounts static assets, defines
Pydantic schemas for request validation, and implements RESTful CRUD endpoints
for managing recipes, ingredients, and instructions via SQLAlchemy persistence.
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
    """Represents an ingredient schema for request validation and API documentation.

    Attributes:
        name: The name of the ingredient (e.g., "Flour").
        dietary_tags: A list of associated dietary tags (e.g., ["VEGAN", "GLUTEN"]).
    """

    name: str = Field(..., example="Flour")
    dietary_tags: List[str] = Field(default=[], example=["VEGAN", "GLUTEN"])


class RecipeIngredientSchema(BaseModel):
    """Pydantic validation schema linking a recipe to an ingredient with quantities.

    Attributes:
        ingredient: The underlying ingredient details (name and dietary tags).
        quantity: The amount of the ingredient required.
        unit: The unit of measurement for the quantity (e.g., "cups", "grams").
    """

    ingredient: IngredientSchema
    quantity: float = Field(default=1.0, example=2.0)
    unit: str = Field(default="", example="cups")


class InstructionSchema(BaseModel):
    """Pydantic validation schema for a recipe preparation step.

    Attributes:
        description: The text describing the action to perform.
        equipment: A list of kitchen tools or equipment needed for the step.
        prep_time: The estimated duration of the step in minutes.
        include_in_prep_time: Whether this step's duration counts
        toward the recipe's total prep time.
    """

    description: str = Field(..., example="Mix ingredients in a bowl.")
    equipment: List[str] = Field(default=[], example=["mixing bowl", "spoon"])
    prep_time: int = Field(default=0, example=5)
    include_in_prep_time: bool = Field(default=True)


class RecipeCreateSchema(BaseModel):
    """Pydantic validation schema for creating or updating a recipe.

    Attributes:
        name: The display name of the recipe.
        recipe_ingredients: A list of ingredients required, including quantities and units.
        instructions: A list of preparation steps detailing how to make the recipe.
    """

    name: str = Field(..., example="Homemade Bread")
    recipe_ingredients: List[RecipeIngredientSchema] = []
    instructions: List[InstructionSchema] = []


@app.get("/", include_in_schema=True)
@app.head("/", include_in_schema=False)
async def read_index():
    """Serve the main frontend user interface HTML page.

    Returns:
        FileResponse: The index.html file from the static assets directory.
    """
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve the favicon.ico file directly from the static assets directory.

    Returns:
        FileResponse: The favicon.ico file from STATIC_DIR.
    """
    return FileResponse(STATIC_DIR / "favicon.ico")


@app.get("/recipes-db", summary="Get recipes from database")
def get_db_recipes(
    name: Optional[str] = Query(
        None, description="Filter by recipe name (partial match)"
    ),
    db: Session = Depends(get_db),
):
    """Fetch recipes from the database, filter by optional name, and render HTML list items.

    Args:
        name: An optional partial name string to filter recipes.
        db: The SQLAlchemy database session dependency.

    Returns:
        HTMLResponse: An HTML string containing list items with recipe links and
        embedded JSON data.
    """
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
            "id": r.id,
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
    """Add a new recipe with ingredients and instructions to the database.

    Args:
        recipe_data: The validated Pydantic schema containing the recipe name,
            ingredients, and preparation steps.
        db: The SQLAlchemy database session dependency.

    Returns:
        dict: A confirmation message along with the created recipe's ID, name,
        and counts of its ingredients and instructions.

    Raises:
        HTTPException: If a recipe with the same name already exists (400)
        or if a database error occurs (400).
    """
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


@app.delete("/recipes/{id}", summary="Delete a recipe by id")
def delete_recipe(id: int, db: Session = Depends(get_db)):
    """Remove a recipe by its unique ID from the database.

    Args:
        id: The primary key ID of the recipe to delete.
        db: The SQLAlchemy database session dependency.

    Returns:
        dict: A confirmation message indicating successful deletion.

    Raises:
        HTTPException: If the recipe ID is not found in the database (404)
        or if a server error occurs during deletion (500).
    """
    db_recipe = db.query(RecipeModel).filter(RecipeModel.id == id).first()
    if not db_recipe:
        raise HTTPException(
            status_code=404,
            detail=f"Recipe with ID '{id}' not found in the database.",
        )

    recipe_name = db_recipe.name
    try:
        db.delete(db_recipe)
        db.commit()
        return {"message": f"Recipe '{recipe_name}' deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/recipes/{id}", summary="Update an existing recipe by id")
def update_recipe(
    id: int, recipe_data: RecipeCreateSchema, db: Session = Depends(get_db)
):
    """Update an existing recipe's name, ingredients, and instructions by ID.

    Args:
        id: The primary key ID of the recipe to update.
        recipe_data: The validated Pydantic schema containing updated recipe
            details, ingredients, and preparation steps.
        db: The SQLAlchemy database session dependency.

    Returns:
        dict: A confirmation message indicating the recipe was updated successfully.

    Raises:
        HTTPException: If the recipe ID is not found (404), if another recipe
        already uses the requested name (400), or if a database error occurs (400).
    """
    db_recipe = db.query(RecipeModel).filter(RecipeModel.id == id).first()
    if not db_recipe:
        raise HTTPException(
            status_code=404,
            detail=f"Recipe with ID '{id}' not found in the database.",
        )

    # Prevent renaming to a name already used by a different recipe
    duplicate = (
        db.query(RecipeModel)
        .filter(RecipeModel.name == recipe_data.name, RecipeModel.id != id)
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=400,
            detail=f"Another recipe named '{recipe_data.name}' already exists.",
        )

    try:
        db_recipe.name = recipe_data.name

        # Replace existing ingredients and instructions (cascade deletes orphans)
        db_recipe.ingredients.clear()
        for ri in recipe_data.recipe_ingredients:
            db_recipe.ingredients.append(
                RecipeIngredientModel(
                    ingredient_name=ri.ingredient.name,
                    quantity=ri.quantity,
                    unit=ri.unit,
                    dietary_tags=",".join(ri.ingredient.dietary_tags),
                )
            )

        db_recipe.instructions.clear()
        for ins in recipe_data.instructions:
            db_recipe.instructions.append(
                InstructionModel(
                    description=ins.description,
                    equipment=",".join(ins.equipment),
                    prep_time=ins.prep_time,
                    include_in_prep_time=ins.include_in_prep_time,
                )
            )

        db.commit()
        db.refresh(db_recipe)
        return {"message": f"Recipe '{db_recipe.name}' updated successfully!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
