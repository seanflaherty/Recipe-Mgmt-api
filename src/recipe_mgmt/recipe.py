"""Defines the Recipe and Instruction domain models for the recipe management system."""

from recipe_mgmt.components import RecipeIngredient


class Instruction:
    """Represents a single preparation step or instruction in a recipe.

    Attributes:
        description: The text describing the action to perform.
        prep_time: The estimated time required for this step in minutes.
        equipment: A list of kitchen tools or equipment needed for the step.
        include_in_prep_time: Whether this step's duration should contribute
            to the recipe's total prep time calculation.
    """

    def __init__(
        self,
        description: str,
        prep_time: int,
        equipment: list[str] | None = None,
        include_in_prep_time: bool = True,
    ) -> None:
        self.description = description
        self.prep_time = prep_time
        self.equipment: list[str] = equipment if equipment is not None else []
        self.include_in_prep_time = include_in_prep_time

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.description!r}, {self.prep_time!r}, "
            f"{self.equipment!r}, {self.include_in_prep_time!r})"
        )

    def __str__(self) -> str:
        return (
            f"{self.description} (Prep time: {self.prep_time} minutes, Equipment: "
            f"{', '.join(self.equipment)})"
        )

    def to_dict(self) -> dict:
        """Convert the instance into a dictionary representation.

        Returns:
            dict: A dictionary containing description, prep_time,
            equipment, and include_in_prep_time.
        """
        return {
            "description": self.description,
            "prep_time": self.prep_time,
            "equipment": self.equipment,
            "include_in_prep_time": self.include_in_prep_time,
        }


class Recipe:
    """Represents a complete recipe, including ingredients, instructions, and metadata.

    Attributes:
        name: The display name of the recipe.
        recipe_ingredients: A list of `RecipeIngredient` associations linking the
            recipe to its required ingredients.
        instructions: A list of `Instruction` objects detailing the preparation steps.

    Properties:
        total_prep_time: Calculates the aggregate preparation time across all
        included instructions. required_equipment: Collects a unique set of all
        equipment needed by the recipe's instructions.
    """

    def __init__(
        self,
        name: str,
        recipe_ingredients: list[RecipeIngredient],
        instructions: list[Instruction] | None = None,
    ) -> None:
        self.name = name
        self.recipe_ingredients = recipe_ingredients
        self.instructions: list[Instruction] = (
            instructions if instructions is not None else []
        )

    def __repr__(self):
        return (
            f"{type(self).__name__}({self.name!r}, {self.recipe_ingredients!r}, "
            f"{self.instructions!r})"
        )

    def __str__(self):
        return self.name

    def get_dietary_tags(self) -> set:
        """Returns a set of dietary tags, if any."""
        if not self.recipe_ingredients:
            return set()

        return set.intersection(
            *(
                recipe_ingredient.ingredient.dietary_tags
                for recipe_ingredient in self.recipe_ingredients
            )
        )

    @property
    def total_prep_time(self) -> int:
        """Calculates and returns the total preparation time for all included instructions."""
        return sum(
            instr.prep_time for instr in self.instructions if instr.include_in_prep_time
        )

    @property
    def required_equipment(self) -> set:
        """Returns the set of equipment required by the instructions of the recipe."""
        return set(eq for instr in self.instructions for eq in instr.equipment)

    def uses_ingredient(self, ingredient_name: str) -> bool:
        """Returns True if the recipe uses an ingredient matching the name."""
        return any(
            ingredient_name.lower() in ri.ingredient.name.lower()
            for ri in self.recipe_ingredients
        )

    def to_dict(self) -> dict:
        """Serialize the recipe into a dictionary format suitable for JSON responses.

        Includes the recipe metadata, ingredients, dietary information, and instruction
        details in a nested structure ready for API serialization."""
        return {
            "name": self.name,
            "total_prep_time": self.total_prep_time,
            "required_equipment": list(self.required_equipment),
            "dietary_tags": [tag.name for tag in self.get_dietary_tags()],
            "recipe_ingredients": [
                {
                    "quantity": ri.quantity,
                    "unit": ri.unit,
                    "ingredient": {
                        "name": ri.ingredient.name,
                        "dietary_tags": [
                            tag.name for tag in ri.ingredient.dietary_tags
                        ],
                    },
                }
                for ri in self.recipe_ingredients
            ],
            "instructions": [ins.to_dict() for ins in self.instructions],
        }
