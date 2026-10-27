"""A module containing the Recipe and related classes."""
from recipe_mgmt.components import RecipeIngredient

class Instruction:
    """A single step or instruction in a recipe."""
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
        return (f"{type(self).__name__}({self.description!r}, {self.prep_time!r}, "
                f"{self.equipment!r}, {self.include_in_prep_time!r})")

    def __str__(self) -> str:
        return (f"{self.description} (Prep time: {self.prep_time} minutes, Equipment: "
                f"{', '.join(self.equipment)})")


class Recipe:
    """Recipe class."""
    def __init__(
        self,
        name: str,
        recipe_ingredients: list[RecipeIngredient],
        instructions: list[Instruction] | None = None,
    ) -> None:
        self.name = name
        self.recipe_ingredients = recipe_ingredients
        self.instructions: list[Instruction] = instructions if instructions is not None else []

    def __repr__(self):
        return (f"{type(self).__name__}({self.name!r}, {self.recipe_ingredients!r}, "
                f"{self.instructions!r})")

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
