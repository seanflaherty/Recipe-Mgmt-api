"""A module to hold Recipe Book and related classes."""
from collections.abc import MutableSequence, Iterable, Iterator
from typing import overload
from recipe_mgmt.recipe import Recipe
from recipe_mgmt.helpers import log_recipe_action

class RecipeBookSearcher:
    """Search recipe book class."""
    def __init__(self, recipes: Iterable[Recipe] | None) -> None:
        self.recipes: list[Recipe] = list(recipes) if recipes is not None else []

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.recipes!r})"

    @staticmethod
    def _matches_query(items, query):
        return any(query.lower() in item.lower() for item in items)

    def by_name(self, query: str) -> Iterator[Recipe]:
        """Search by name, returns matching recipe(s)."""
        return (
            recipe
            for recipe in self.recipes
            if self._matches_query([recipe.name], query)
        )

    def by_ingredient(self, query: str) -> Iterator[Recipe]:
        """Search by ingredient, returns matching recipe(s)."""
        return (
            recipe
            for recipe in self.recipes
            if any(
                self._matches_query([ri.ingredient.name], query)
                for ri in recipe.recipe_ingredients
            )
        )

    def by_dietary_tag(self, query: str) -> Iterator[Recipe]:
        """Search by dietary tag, returns matching recipe(s)."""
        return (
            recipe
            for recipe in self.recipes
            if any(
                query.lower() in tag.name.lower() for tag in recipe.get_dietary_tags()
            )
        )

    def by_max_prep_time(self, max_minutes: int) -> Iterator[Recipe]:
        """Search by total prep time, returns matching recipe(s)."""
        return (
            recipe for recipe in self.recipes if recipe.total_prep_time <= max_minutes
        )

    def filter(
        self,
        name: str | None = None,
        ingredient: str | None = None,
        dietary_tag: str | None = None,
        max_prep_time: int | None = None,
    ) -> Iterator[Recipe]:
        """Filter recipes based on optional criteria."""
        for recipe in self.recipes:
            if name and not self._matches_query([recipe.name], name):
                continue
            if ingredient and not any(
                self._matches_query([ri.ingredient.name], ingredient)
                for ri in recipe.recipe_ingredients
            ):
                continue
            if dietary_tag and not any(
                dietary_tag.lower() in tag.name.lower()
                for tag in recipe.get_dietary_tags()
            ):
                continue
            if max_prep_time and recipe.total_prep_time > max_prep_time:
                continue
            yield recipe


class RecipeBook(MutableSequence[Recipe]):
    """A mutable collection container representing a book of recipes.

    Inherits from MutableSequence to provide standard list-like behaviors
    along with specialized search and filtering capabilities.
    """
    def __init__(self, name: str, recipes: Iterable[Recipe] | None = None) -> None:
        """Initialize a RecipeBook instance.

        Args:
            name: The title or name of the recipe book.
            recipes: An optional iterable of initial Recipe objects to populate the book.
        """
        self.name = name
        self.recipes: list[Recipe] = list(recipes) if recipes is not None else []
        self.searcher: RecipeBookSearcher = RecipeBookSearcher(self.recipes)

    def __repr__(self) -> str:
        """Return an official string representation of the RecipeBook."""
        return f"{type(self).__name__}({self.name!r}, {self.recipes!r})"

    def __str__(self) -> str:
        """Return a user-friendly string representation of the RecipeBook."""
        return f"RecipeBook: {self.name} with {len(self.recipes)} recipes"

    def __len__(self) -> int:
        """Return the total number of recipes in the book."""
        return len(self.recipes)

    @overload
    def __getitem__(self, index: int) -> Recipe:
        ...

    @overload
    def __getitem__(self, index: slice) -> list[Recipe]:
        """Retrieve a recipe or slice of recipes by index."""
        return self.recipes[index]

    def __getitem__(self, index: int | slice) -> Recipe | list[Recipe]:
        """Retrieve a recipe or slice of recipes by index."""
        return self.recipes[index]

    @overload
    def __setitem__(self, index: int, value: Recipe) -> None:
        ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[Recipe]) -> None:
        ...

    def __setitem__(self, index: int | slice, value: Recipe | Iterable[Recipe]) -> None:
        """Set or replace a recipe or slice of recipes at a specific index."""
        if isinstance(index, slice):
            recipes_to_add = list(value) if isinstance(value, Iterable) else [value]
            for item in recipes_to_add:
                if not isinstance(item, Recipe):
                    raise ValueError("Only Recipe instances can be added")
            self.recipes[index] = recipes_to_add
        else:
            if not isinstance(value, Recipe):
                raise ValueError("Only Recipe instances can be added")
            self.recipes[index] = value

    def __delitem__(self, index: int | slice) -> None:
        """Delete a recipe or slice of recipes by index."""
        del self.recipes[index]

    def __iter__(self) -> Iterator[Recipe]:
        """Return an iterator over the recipes in the book."""
        return iter(self.recipes)

    def insert(self, index: int, recipe: Recipe) -> None:
        """Insert a recipe at a specific index.

        Args:
            index: The numeric position to insert at.
            recipe: The Recipe instance to insert.

        Raises:
            ValueError: If the item is not a Recipe instance or already exists in the book.
        """
        if not isinstance(recipe, Recipe):
            raise ValueError("Only Recipe instances can be added")
        if recipe in self.recipes:
            raise ValueError("Recipe already exists in the book")
        self.recipes.insert(index, recipe)

    @log_recipe_action("add")
    def append(self, recipe: Recipe) -> None:
        """Append a new recipe to the end of the book.

        Args:
            recipe: The Recipe instance to append.
        """
        self.insert(len(self.recipes), recipe)

    @log_recipe_action("remove")
    def remove(self, recipe: Recipe) -> None:
        """Remove a specific recipe instance from the book.

        Args:
            recipe: The Recipe instance to remove.

        Raises:
            ValueError: If the recipe is not found in the book.
        """
        if recipe in self.recipes:
            self.recipes.remove(recipe)
        else:
            raise ValueError("Recipe not found in the book")

    def remove_by_name(self, name: str) -> None:
        """Remove the first recipe matching the exact name.

        Args:
            name: The exact name of the recipe to remove.
        """
        for recipe in self.recipes:
            if recipe.name == name:
                self.recipes.remove(recipe)
                return

    def remove_by_partial_name(self, partial_name: str, force: bool = False) -> None:
        """Remove a recipe by partial name match.

        Args:
            partial_name: A substring to match against recipe names.
            force: If True, bypasses errors when multiple matches are found.

        Raises:
            ValueError: If no recipes match, or if multiple matches occur and force is False.
        """
        matches: list[Recipe] = list(self.search_by_name(partial_name))

        if not matches:
            raise ValueError(
                f"No recipes found with name containing '{partial_name}'")

        if len(matches) > 1 and not force:
            names = ", ".join(recipe.name for recipe in matches)
            raise ValueError(
                f"Multiple recipes found with name containing '{names}'"
            )

        self.recipes.remove(matches[0])

    def search_by_name(self, query: str) -> Iterator[Recipe]:
        """Search recipes by name query.

        Args:
            query: The search term for recipe names.

        Returns:
            An iterator yielding matching Recipe instances.
        """
        return self.searcher.by_name(query)

    def search_by_ingredient(self, query):
        """Search recipes by ingredient query.

        Args:
            query: The search term for ingredients.

        Returns:
            An iterator yielding matching Recipe instances.
        """
        return self.searcher.by_ingredient(query)

    def search_by_dietary_tag(self, query):
        """Search recipes by dietary tag query.

        Args:
            query: The dietary tag search term.

        Returns:
            An iterator yielding matching Recipe instances.
        """
        return self.searcher.by_dietary_tag(query)

    def search_by_max_prep_time(self, max_minutes):
        """Search recipes by maximum total preparation time.

        Args:
            max_minutes: The maximum allowable prep time in minutes.

        Returns:
            An iterator yielding matching Recipe instances.
        """
        return self.searcher.by_max_prep_time(max_minutes)

    def search_by_multiple_criteria(
        self,
        name: str | None = None,
        ingredient: str | None = None,
        dietary_tag: str | None = None,
        max_prep_time: int | None = None
    ):
        """Filter recipes based on multiple optional criteria.

        Args:
            name: Optional partial name query.
            ingredient: Optional ingredient query.
            dietary_tag: Optional dietary tag query.
            max_prep_time: Optional maximum preparation time limit in minutes.

        Returns:
            An iterator yielding matching Recipe instances.
        """
        return self.searcher.filter(name, ingredient, dietary_tag, max_prep_time)


# TODO
# class VegetarianRecipeBook(RecipeBook):
#     def __init__(self):
#         ...

#     def check_dietary_tags(self):
#         # Should this method be defined here?
#         ...
