import pytest
from recipe_mgmt.components import(
    DietaryTag,
    Ingredient,
    RecipeIngredient,
    IngredientRepository,
)

def test_dietary_tag_values():
    """Test that dietary tags are valid string enums."""
    assert DietaryTag.GLUTEN_FREE == "gluten_free"
    assert DietaryTag.NUT_FREE == "nut_free"
    assert isinstance(DietaryTag.GLUTEN_FREE, str)
