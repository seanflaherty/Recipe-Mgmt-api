"""Main application module for the Recipe Management API.

This module initializes the Connexion 3.x application, loads the OpenAPI
specification contract (`recipe_mgmt.openapi.yaml`)[cite: 3, 6], and defines the core HTTP
request handler functions (`get_recipes`, `add_recipe`, and `delete_recipe`).

It acts as the bridge between the web interface (Swagger UI)[cite: 4, 7],
the underlying domain logic (`RecipeBook`)[cite: 3], and disk persistence (`storage.py`)[cite: 10],
exposing a fully-compatible ASGI `application` instance for Uvicorn[cite: 3].
"""
from pathlib import Path
import connexion
from recipe_mgmt.components import DietaryTag, Ingredient, RecipeIngredient
from recipe_mgmt.recipe import Instruction, Recipe
from recipe_mgmt.recipe_book import RecipeBook
from recipe_mgmt.storage import select_loader

# Initialize a shared RecipeBook instance for the app
recipe_book = RecipeBook("My Recipe Collection", recipes=[])

def get_recipes(
        name: str | None = None,
        ingredient: str | None  = None,
        dietary_tag: str | None  = None,
        max_prep_time: int | None  = None):
    """Fetch or filter recipes and serialize them into dictionaries."""
    results = recipe_book.search_by_multiple_criteria(
        name=name,
        ingredient=ingredient,
        dietary_tag=dietary_tag,
        max_prep_time=max_prep_time
    )

    # Convert each Recipe object into a dictionary/json-serializable format
    recipe_list = []
    for recipe in results:
        # Check if Pydantic model_dump is available, otherwise fallback to dict or vars
        if hasattr(recipe, "model_dump"):
            recipe_list.append(recipe.model_dump())
        elif hasattr(recipe, "dict"):
            recipe_list.append(recipe.dict())
        else:
            recipe_list.append(vars(recipe))

    return recipe_list, 200

def add_recipe(body: dict):
    """Add a new recipe to the recipe book and save it as a CSV file."""
    try:
        name = body.get("name", "")

        # 1. Parse raw ingredient dictionaries into domain objects
        recipe_ingredients = []
        for ri in body.get("recipe_ingredients", []):
            ing_data = ri.get("ingredient", {})
            raw_tags = ing_data.get("dietary_tags", [])

            tags = set()
            for t in raw_tags:
                if isinstance(t, dict):
                    tag_name = t.get("name", "")
                else:
                    tag_name = str(t)
                if tag_name:
                    tags.add(DietaryTag[tag_name.upper()])

            ingredient = Ingredient(
                name=ing_data.get("name", ""),
                dietary_tags=tags
            )
            recipe_ingredients.append(
                RecipeIngredient(
                    ingredient=ingredient,
                    quantity=ri.get("quantity", 1),
                    unit=ri.get("unit", "")
                )
            )

        # 2. Parse raw instruction dictionaries into domain objects
        instructions = []
        for ins in body.get("instructions", []):
            instructions.append(
                Instruction(
                    description=ins.get("description", ""),
                    prep_time=ins.get("prep_time", 0),
                    equipment=ins.get("equipment", []),
                    include_in_prep_time=ins.get("include_in_prep_time", True)
                )
            )

        # 3. Instantiate the Recipe domain model with real objects
        recipe = Recipe(
            name=name,
            recipe_ingredients=recipe_ingredients,
            instructions=instructions
        )

        # 4. Add to the in-memory book
        recipe_book.append(recipe)

        # 5. Persist to CSV using the storage module
        loader = select_loader("csv")
        filename = f"{recipe.name.lower().replace(' ', '_')}.csv"
        destination = Path("src\\recipe_mgmt\\recipes") / filename
        loader.save_data(destination, recipe)

        return {
            "message": "Recipe added and saved to CSV successfully",
            "name": recipe.name,
            "file": str(destination)
        }, 201

    except (ValueError, TypeError, KeyError, IOError) as e:
        return {"error": str(e)}, 400

def delete_recipe(name: str):
    """Remove a recipe by name from the recipe book."""
    try:
        recipe_book.remove_by_name(name)
        return {"message": f"Recipe '{name}' deleted successfully"}, 200
    except ValueError as e:
        return {"error": str(e)}, 404

