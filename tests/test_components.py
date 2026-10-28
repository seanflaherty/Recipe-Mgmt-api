"""Unit tests for the recipe_mgmt.components module."""
import pytest
from recipe_mgmt.components import(
    DietaryTag,
    Ingredient,
    RecipeIngredient,
    IngredientRepository,
)

def test_dietary_tag_enum() -> None:
    """Test that dietary tags are valid string enums."""
    assert DietaryTag.GLUTEN_FREE == "gluten_free"
    assert DietaryTag.NUT_FREE == "nut_free"
    assert isinstance(DietaryTag.GLUTEN_FREE, str)

def test_ingredient_creation() -> None:
    """Test creating an Ingredient with and without dietary tags."""
    # Without tags (defaults to empty set)
    ing1 = Ingredient(name="Flour")
    assert ing1.name == "Flour"
    assert ing1.dietary_tags == set()

    # With tags
    tags = {DietaryTag.GLUTEN_FREE, DietaryTag.NUT_FREE}
    ing2 = Ingredient(name="Almond Flour", dietary_tags=tags)
    assert ing2.name == "Almond Flour"
    assert ing2.dietary_tags == tags

def test_recipe_ingredient_behavior() -> None:
    """Test RecipeIngredient properties, string formatting, and tag delegation."""
    ingredient = Ingredient(name="Sugar", dietary_tags={DietaryTag.GLUTEN_FREE})
    ri = RecipeIngredient(ingredient=ingredient, quantity=1.5, unit="cups")

    # Attributes
    assert ri.ingredient == ingredient
    assert ri.quantity == 1.5
    assert ri.unit == "cups"

    # Delegation of dietary tags
    assert ri.dietary_tags == {DietaryTag.GLUTEN_FREE}

    # String and representation formats
    assert str(ri) == "1.5 cups of Sugar"
    assert repr(ri) == "RecipeIngredient('Sugar', 1.5, 'cups')"

def test_ingredient_repository_initialization() -> None:
    """Test repository string and representation outputs."""
    repo = IngredientRepository(name="Pantry")
    assert repo.name == "Pantry"
    assert str(repo) == "IngredientRepository: Pantry with 0 ingredients"
    assert repr(repo) == "IngredientRepository('Pantry')"

def test_ingredient_repository_add_and_access() -> None:
    """Test adding ingredients and case-insensitive attribute access."""
    repo = IngredientRepository(name="Pantry")
    flour = Ingredient(name="Flour")
    sugar = Ingredient(name="Sugar")

    repo.add_ingredient(flour)
    repo.add_ingredient(sugar)

    # Case-insensitive attribute access (__getattr__)
    assert repo.flour == flour
    assert repo.FLOUR == flour
    assert repo.sugar == sugar

def test_ingredient_repository_duplicate_raises_error() -> None:
    """Test that adding an existing ingredient (case-insensitively) raises ValueError."""
    repo = IngredientRepository(name="Pantry")
    repo.add_ingredient(Ingredient(name="Salt"))

    # Attempting to add duplicate with different casing
    with pytest.raises(ValueError, match="Ingredient already exists"):
        repo.add_ingredient(Ingredient(name="SALT"))


def test_ingredient_repository_missing_attribute_raises_error() -> None:
    """Test that accessing a non-existent ingredient raises AttributeError."""
    repo = IngredientRepository(name="Pantry")

    with pytest.raises(AttributeError, match="Ingredient not found"):
        _ = repo.nonexistent_ingredient
