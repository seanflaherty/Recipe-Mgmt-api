"""Domain models and repository management for recipe ingredients.

This module provides core data structures and repository patterns for handling
ingredients, dietary classifications, recipe quantities, and storage collections
within the recipe management application.

Classes:
    DietaryTag: Enumeration of standard dietary restriction tags.
    Ingredient: Represents a base ingredient with associated dietary tags.
    RecipeIngredient: Links an ingredient with a specific quantity and measurement unit.
    IngredientRepository: Case-insensitive container for managing ingredient collections.
"""
from dataclasses import dataclass, field
from enum import StrEnum, auto

# Ingredients and Dietary Requirements
class DietaryTag(StrEnum):
    """Enum for dietary tags."""
    GLUTEN_FREE = auto()
    NUT_FREE = auto()

@dataclass
class Ingredient:
    """Class for the ingredients of the recipe."""
    name: str
    dietary_tags: set[DietaryTag] = field(default_factory=set)


class RecipeIngredient:
    """Represents a specific ingredient, quantity, and unit used in a recipe.

    Attributes:
        ingredient (Ingredient): The underlying ingredient object.
        quantity (int | float): The numerical amount required.
        unit (str): The unit of measurement (e.g., "cups", "grams", "tbsp").
        dietary_tags: Dietary tags inherited or associated with the ingredient.
    """
    def __init__(
        self,
        ingredient: Ingredient,
        quantity: int | float,
        unit: str,
    ):
        self.ingredient = ingredient
        self.quantity = quantity
        self.unit = unit

    def __repr__(self):
        return f"{type(self).__name__}({self.ingredient.name!r}, {self.quantity!r}, {self.unit!r})"

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name}"

    @property
    def dietary_tags(self) -> set[DietaryTag]:
        """Get the dietary tags associated with the underlying ingredient."""
        return self.ingredient.dietary_tags

    @dietary_tags.setter
    def dietary_tags(self, value):
        self._dietary_tags = value

class IngredientRepository:
    """A repository for managing a collection of ingredients.

    Provides storage, duplicate prevention, and convenient attribute-based
    access to ingredients in a case-insensitive manner.

    Attributes:
        name (str): The name or identifier of the repository.
    """
    def __init__(self, name: str) -> None:
        """Initialize a new IngredientRepository instance.

        Args:
            name (str): The name or identifier for this repository.
        """
        self.name = name
        self._ingredients: dict[str, Ingredient] = {}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"

    def __str__(self) -> str:
        return f"IngredientRepository: {self.name} with {len(self._ingredients)} ingredients"

    def add_ingredient(self, ingredient: Ingredient) -> None:
        """Add an ingredient to the repository.

        Args:
            ingredient (Ingredient): The ingredient object to add.

        Raises:
            ValueError: If an ingredient with the same name already exists.
        """
        if ingredient.name.upper() in self._ingredients:
            raise ValueError("Ingredient already exists")
        self._ingredients[ingredient.name.upper()] = ingredient

    def __getattr__(self, name):
        """Allow attribute-style access to ingredients by name (case-insensitive).

        Example:
            repo.flour or repo.FLOUR returns the flour Ingredient object.

        Raises:
            AttributeError: If the ingredient does not exist in the repository.
        """
        name = name.upper()
        if name in self._ingredients:
            return self._ingredients[name]
        raise AttributeError("Ingredient not found")
