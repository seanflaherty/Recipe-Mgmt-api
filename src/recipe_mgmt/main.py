from fastapi import FastAPI
from pydantic import BaseModel
from .recipe_book import RecipeBook
import connexion

# SCF app = FastAPI()
app = connexion.App(__name__, specification_dir="./")
app.add_api("recipe_mgmt.openapi.yaml", options={"swagger_ui": True}) # Make sure this file exists and contains paths!
application = app.app # Exposes the underlying Starlette/FastAPI app for Uvicorn

# Initialize your recipe book on startup
# SCF app.state.recipe_book = RecipeBook("My Favorites", recipes=[...])

def get_recipes():
    # Access your recipe book from app state or handle the logic here
    return [{"name": "Pancakes"}, {"name": "Waffles"}]