"""Main application module for the Recipe Management API.

This module initializes the FastAPI application and defines core HTTP
request handler functions (`get_recipes`, `add_recipe`, and `delete_recipe`),
managing in-memory state and disk persistence (`storage.py`).
"""

from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from recipe_mgmt.components import DietaryTag, Ingredient, RecipeIngredient
from recipe_mgmt.recipe import Instruction, Recipe
from recipe_mgmt.recipe_book import RecipeBook
from recipe_mgmt.storage import select_loader
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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows all origins (adjust to specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


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
    prep_time: int = Field(default=0, example=5)
    equipment: List[str] = Field(default=[], example=["mixing bowl", "spoon"])
    include_in_prep_time: bool = Field(default=True)


class RecipeCreateSchema(BaseModel):
    name: str = Field(..., example="Homemade Bread")
    recipe_ingredients: List[RecipeIngredientSchema] = []
    instructions: List[InstructionSchema] = []


class RecipeRowSchema(BaseModel):
    type: str = Field(..., example="ingredient")  # "ingredient" or "instruction"
    ingredient_name: Optional[str] = Field(None, example="Bread")
    quantity: Optional[float] = Field(None, example=3.0)
    unit: Optional[str] = Field(None, example="slices")
    dietary_tags: Optional[str] = Field(None, example="VEGETARIAN")
    instruction: Optional[str] = Field(None, example="-")
    prep_time: Optional[int] = Field(None, example=0)
    equipment: Optional[str] = Field(None, example="-")
    include_in_prep_time: Optional[bool] = Field(True, example=True)


class FlatRecipeImportSchema(BaseModel):
    recipe_name: str = Field(..., example="Caramelized Onion Toast")
    rows: List[RecipeRowSchema]


# Initialize a shared RecipeBook instance for the app
recipe_book = RecipeBook("My Recipe Collection", recipes=[])


@app.get("/recipes-db", summary="Get recipes from database")
def get_db_recipes(
    name: Optional[str] = Query(
        None, description="Filter by recipe name (partial match)"
    ),
    max_prep_time: Optional[int] = Query(
        None, description="Filter by maximum preparation time in minutes"
    ),
    db: Session = Depends(get_db),
):
    """Fetch all recipes from the configured database with optional query filters."""
    query = db.query(RecipeModel)

    # Apply name filter if provided (case-insensitive substring match)
    if name:
        query = query.filter(RecipeModel.name.ilike(f"%{name}%"))

    # Apply max prep time filter if provided (assuming your RecipeModel has a prep_time column)
    if max_prep_time is not None:
        query = query.filter(RecipeModel.prep_time <= max_prep_time)

    recipes = query.all()

    # Return serialized database records
    return [
        {
            "id": r.id,
            "name": r.name,
            # TODO Include other model attributes as needed
        }
        for r in recipes
    ]


@app.post("/recipes", status_code=201, summary="Add a recipe to the database")
def add_recipe(recipe_data: RecipeCreateSchema, db: Session = Depends(get_db)):
    """Add a new recipe to the database and optionally keep CSV persistence."""
    try:
        # 1. Check if a recipe with this name already exists
        existing_recipe = (
            db.query(RecipeModel).filter(RecipeModel.name == recipe_data.name).first()
        )
        if existing_recipe:
            raise HTTPException(
                status_code=400,
                detail=f"Recipe '{recipe_data.name}' already exists in the database.",
            )

        # 2. Create the main Recipe database record
        db_recipe = RecipeModel(name=recipe_data.name)

        # 3. Add ingredients
        for ri in recipe_data.recipe_ingredients:
            tags_str = ",".join(ri.ingredient.dietary_tags)
            db_ingredient = RecipeIngredientModel(
                ingredient_name=ri.ingredient.name,
                quantity=ri.quantity,
                unit=ri.unit,
                dietary_tags=tags_str,
            )
            db_recipe.ingredients.append(db_ingredient)

        # 4. Add instructions
        for ins in recipe_data.instructions:
            db_instruction = InstructionModel(
                description=ins.description,
                prep_time=ins.prep_time,
                include_in_prep_time=ins.include_in_prep_time,
            )
            db_recipe.instructions.append(db_instruction)

        # 5. Commit to database (SQLite or PostgreSQL)
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)

        # (Optional) Keep your legacy CSV file export if you still want local flat-file backups
        try:
            loader = select_loader("csv")
            filename = f"{recipe_data.name.lower().replace(' ', '_')}.csv"
            destination = Path("src/recipe_mgmt/recipes") / filename
            # Reconstruct domain model for CSV export if needed, or skip if fully moving to DB
        except Exception:
            pass

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
def delete_recipe(name: str):
    """Remove a recipe by name from the recipe book."""
    try:
        recipe_book.remove_by_name(name)
        return {"message": f"Recipe '{name}' deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post(
    "/recipes/import-flat",
    status_code=201,
    summary="Add recipe using flat tabular rows",
)
def import_flat_recipe(payload: FlatRecipeImportSchema, db: Session = Depends(get_db)):
    """Accepts a recipe name and a list of tabular rows (ingredients/instructions)
    and saves them directly to PostgreSQL or SQLite.
    """
    try:
        existing = (
            db.query(RecipeModel)
            .filter(RecipeModel.name == payload.recipe_name)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Recipe '{payload.recipe_name}' already exists.",
            )

        db_recipe = RecipeModel(name=payload.recipe_name)

        for row in payload.rows:
            if (
                row.type.lower() == "ingredient"
                and row.ingredient_name
                and row.ingredient_name != "-"
            ):
                db_recipe.ingredients.append(
                    RecipeIngredientModel(
                        ingredient_name=row.ingredient_name,
                        quantity=row.quantity or 1.0,
                        unit=row.unit or "",
                        dietary_tags=row.dietary_tags or "",
                    )
                )
            elif (
                row.type.lower() == "instruction"
                and row.instruction
                and row.instruction != "-"
            ):
                db_recipe.instructions.append(
                    InstructionModel(
                        description=row.instruction,
                        prep_time=row.prep_time or 0,
                        include_in_prep_time=(
                            row.include_in_prep_time
                            if row.include_in_prep_time is not None
                            else True
                        ),
                    )
                )

        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)

        return {
            "message": "Flat recipe imported and saved successfully!",
            "id": db_recipe.id,
            "name": db_recipe.name,
            "ingredients_added": len(db_recipe.ingredients),
            "instructions_added": len(db_recipe.instructions),
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
