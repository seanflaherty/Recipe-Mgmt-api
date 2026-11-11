"""Main application module for the Recipe Management API.

This module initializes the FastAPI application and defines core HTTP
request handler functions (`get_recipes`, `add_recipe`, and `delete_recipe`),
managing in-memory state and disk persistence (`storage.py`).
"""

from typing import Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from recipe_mgmt.components import DietaryTag, Ingredient, RecipeIngredient
from recipe_mgmt.recipe import Instruction, Recipe
from recipe_mgmt.recipe_book import RecipeBook
from recipe_mgmt.storage import select_loader

app = FastAPI(
    title="Recipe Management API",
    version="1.0.0",
    docs_url="/ui",  # Keeps the UI path.
    redoc_url=None,
)


# Initialize a shared RecipeBook instance for the app
recipe_book = RecipeBook("My Recipe Collection", recipes=[])


@app.get("/recipes", summary="Search or filter recipes")
def get_recipes(
    name: Optional[str] = Query(None, description="Filter by recipe name"),
    ingredient: Optional[str] = Query(None, description="Filter by ingredient"),
    dietary_tag: Optional[str] = Query(None, description="Filter by dietary tag"),
    max_prep_time: Optional[int] = Query(
        None, description="Maximum prep time in minutes"
    ),
):
    """Fetch or filter recipes and serialize them into dictionaries."""
    results = recipe_book.search_by_multiple_criteria(
        name=name,
        ingredient=ingredient,
        dietary_tag=dietary_tag,
        max_prep_time=max_prep_time,
    )

    recipe_list = []
    for recipe in results:
        if hasattr(recipe, "model_dump"):
            recipe_list.append(recipe.model_dump())
        elif hasattr(recipe, "dict"):
            recipe_list.append(recipe.dict())
        else:
            recipe_list.append(vars(recipe))

    return recipe_list


@app.post("/recipes", status_code=201, summary="Add a recipe")
def add_recipe(body: dict):
    """Add a new recipe to the recipe book and save it as a CSV file."""
    try:
        name = body.get("name", "")

        # Parse raw ingredient dictionaries into domain objects
        recipe_ingredients = []
        for ri in body.get("recipe_ingredients", []):
            ing_data = ri.get("ingredient", {})
            raw_tags = ing_data.get("dietary_tags", [])

            tags = set()
            for t in raw_tags:
                tag_name = t.get("name", "") if isinstance(t, dict) else str(t)
                if tag_name:
                    tags.add(DietaryTag[tag_name.upper()])

            ingredient = Ingredient(name=ing_data.get("name", ""), dietary_tags=tags)
            recipe_ingredients.append(
                RecipeIngredient(
                    ingredient=ingredient,
                    quantity=ri.get("quantity", 1),
                    unit=ri.get("unit", ""),
                )
            )

        # Parse raw instruction dictionaries into domain objects
        instructions = [
            Instruction(
                description=ins.get("description", ""),
                prep_time=ins.get("prep_time", 0),
                equipment=ins.get("equipment", []),
                include_in_prep_time=ins.get("include_in_prep_time", True),
            )
            for ins in body.get("instructions", [])
        ]

        # Instantiate the Recipe domain model
        recipe = Recipe(
            name=name, recipe_ingredients=recipe_ingredients, instructions=instructions
        )

        # Add to the in-memory book
        recipe_book.append(recipe)

        # Persist to CSV using the storage module
        loader = select_loader("csv")
        filename = f"{recipe.name.lower().replace(' ', '_')}.csv"
        destination = Path("src/recipe_mgmt/recipes") / filename
        loader.save_data(destination, recipe)

        return {
            "message": "Recipe added and saved to CSV successfully",
            "name": recipe.name,
            "file": str(destination),
        }

    except (ValueError, TypeError, KeyError, IOError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/recipes/{name}", summary="Delete a recipe by name")
def delete_recipe(name: str):
    """Remove a recipe by name from the recipe book."""
    try:
        recipe_book.remove_by_name(name)
        return {"message": f"Recipe '{name}' deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
