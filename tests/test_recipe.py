"""Unit tests for the recipe_mgmt.recipe module."""

from recipe_mgmt.components import DietaryTag, Ingredient, RecipeIngredient
from recipe_mgmt.recipe import Instruction, Recipe

def test_instruction_creation_defaults() -> None:
    """Test Instruction initialization with default values[cite: 6]."""
    inst = Instruction(description="Chop onions", prep_time=5)
    assert inst.description == "Chop onions"
    assert inst.prep_time == 5
    assert inst.equipment == []
    assert inst.include_in_prep_time is True
    assert str(inst) == "Chop onions (Prep time: 5 minutes, Equipment: )"

def test_instruction_custom_attributes() -> None:
    """Test Instruction initialization with all custom values[cite: 6]."""
    inst = Instruction(
        description="Bake bread",
        prep_time=30,
        equipment=["oven", "baking sheet"],
        include_in_prep_time=False,
    )
    assert inst.equipment == ["oven", "baking sheet"]
    assert inst.include_in_prep_time is False
    assert "oven, baking sheet" in str(inst)

def test_recipe_creation_and_basic_methods() -> None:
    """Test Recipe initialization, string formatting, and default instructions[cite: 6]."""
    ing = RecipeIngredient(Ingredient("Flour"), 2.0, "cups")
    recipe = Recipe(name="Simple Bread", recipe_ingredients=[ing])

    assert recipe.name == "Simple Bread"
    assert recipe.recipe_ingredients == [ing]
    assert recipe.instructions == []
    assert str(recipe) == "Simple Bread"


def test_recipe_total_prep_time() -> None:
    """Test calculation of total prep time considering the include_in_prep_time flag[cite: 6]."""
    inst1 = Instruction(description="Mix", prep_time=10, include_in_prep_time=True)
    inst2 = Instruction(description="Rest", prep_time=60, include_in_prep_time=False)
    inst3 = Instruction(description="Knead", prep_time=15, include_in_prep_time=True)

    recipe = Recipe(
        name="Test Bread",
        recipe_ingredients=[],
        instructions=[inst1, inst2, inst3],
    )
    # Total time should only sum instructions where include_in_prep_time is True (10 + 15)
    assert recipe.total_prep_time == 25

def test_recipe_required_equipment() -> None:
    """Test gathering unique required equipment across all instructions[cite: 6]."""
    inst1 = Instruction(description="Step 1", prep_time=5, equipment=["bowl", "spoon"])
    inst2 = Instruction(description="Step 2", prep_time=5, equipment=["bowl", "pan"])

    recipe = Recipe(
        name="Test Equipment",
        recipe_ingredients=[],
        instructions=[inst1, inst2],
    )
    # Should compile a unique set of equipment items
    assert recipe.required_equipment == {"bowl", "spoon", "pan"}


def test_recipe_get_dietary_tags() -> None:
    """Test the intersection of dietary tags across all recipe ingredients[cite: 6]."""
    ing1 = Ingredient(name="Almond Flour",
                       dietary_tags={DietaryTag.GLUTEN_FREE, DietaryTag.NUT_FREE})
    ing2 = Ingredient(name="Rice Flour", dietary_tags={DietaryTag.GLUTEN_FREE})

    ri1 = RecipeIngredient(ing1, 1.0, "cup")
    ri2 = RecipeIngredient(ing2, 0.5, "cup")

    recipe = Recipe(
        name="Gluten-Free Treat",
        recipe_ingredients=[ri1, ri2],
    )
    # Intersection should only be GLUTEN_FREE since both share it, but not NUT_FREE
    assert recipe.get_dietary_tags() == {DietaryTag.GLUTEN_FREE}


def test_recipe_get_dietary_tags_empty() -> None:
    """Test that dietary tags return an empty set when there are no ingredients[cite: 6]."""
    recipe = Recipe(name="Empty Recipe", recipe_ingredients=[])
    assert recipe.get_dietary_tags() == set()


def test_uses_ingredient() -> None:
    """Test case-insensitive ingredient lookup by name substring[cite: 6]."""
    ing = Ingredient(name="Organic Whole Milk")
    ri = RecipeIngredient(ing, 1.0, "cup")
    recipe = Recipe(name="Pancakes", recipe_ingredients=[ri])

    assert recipe.uses_ingredient("milk") is True
    assert recipe.uses_ingredient("WHOLE") is True
    assert recipe.uses_ingredient("organic whole milk") is True
    assert recipe.uses_ingredient("almond milk") is False
