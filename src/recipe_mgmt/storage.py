"""Module for loading and saving recipe data from various storage formats."""
from abc import ABC, abstractmethod
import csv
from pathlib import Path
from typing import Any, Generic, TypeVar

from recipe_mgmt.components import DietaryTag, Ingredient, RecipeIngredient
from recipe_mgmt.recipe import Instruction, Recipe

# Generic type variable for the payload handled by loaders
T = TypeVar("T")


class DataLoader(ABC, Generic[T]):
    """Abstract base class defining an interface for loading and saving data."""

    @abstractmethod
    def load_data(self, source: str | Path, **kwargs: Any) -> T:
        """Load data from a specified source.

        Args:
            source: The file path or identifier to load from.
            **kwargs: Additional backend-specific loading options.

        Returns:
            The loaded data payload of type T.
        """

    @abstractmethod
    def save_data(self, destination: str | Path, data: T, **kwargs: Any) -> None:
        """Save data to a specified destination.

        Args:
            destination: The file path or identifier to save to.
            data: The data payload of type T to save.
            **kwargs: Additional backend-specific saving options.
        """


class CSVDataLoader(DataLoader[Recipe]):
    """Data loader implementation for reading and writing recipes via CSV files."""

    def load_data(self, source: str | Path, **kwargs: Any) -> Recipe:
        """Load a single Recipe from a structured CSV file[cite: 3].

        Args:
            source: Path to the CSV file.
            **kwargs: Additional keyword arguments.

        Returns:
            A populated Recipe instance.
        """
        filepath = Path(source)
        name = filepath.stem
        name = name.replace("_", " ").title()  # Assumes file names use underscores[cite: 3]
        ingredients: list[RecipeIngredient] = []
        instructions: list[Instruction] = []

        with filepath.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_type = row.get("type", "").strip().lower()
                if row_type == "ingredient":
                    dietary_tags = {
                        DietaryTag[tag.strip()]
                        for tag in row["dietary_tags"].split(";")
                        if tag.strip()
                    }
                    ingredient = Ingredient(
                        row["ingredient_name"],
                        dietary_tags,
                    )
                    ingredients.append(
                        RecipeIngredient(
                            ingredient,
                            float(row["quantity"]),
                            row["unit"],
                        )
                    )
                elif row_type == "instruction":
                    equipment = [
                        item.strip()
                        for item in row["equipment"].split(";")
                        if item.strip()
                    ]
                    instructions.append(
                        Instruction(
                            row["instruction"],
                            int(row["prep_time"]),
                            equipment,
                            row["include_in_prep_time"].strip().lower() == "true",
                        )
                    )

        return Recipe(name, ingredients, instructions)

    def load_all(self, folderpath: str | Path) -> list[Recipe]:
        """Load all recipe CSV files from a given directory.

        Args:
            folderpath: Path to the directory containing CSV files.

        Returns:
            A list of loaded Recipe instances.
        """
        folder = Path(folderpath)
        return [self.load_data(file) for file in folder.glob("*.csv")]

    def save_data(self, destination: str | Path, data: Recipe, **kwargs: Any) -> None:
        """Save a Recipe instance to a CSV destination.

        Args:
            destination: Path where the CSV file should be written.
            data: The Recipe instance to save.
            **kwargs: Additional keyword arguments.
        """
        # Implementation for saving CSV data


class JSONDataLoader(DataLoader[Recipe]):
    """Data loader implementation for reading and writing recipes via JSON files."""

    def load_data(self, source: str | Path, **kwargs: Any) -> Recipe:
        """Load a Recipe from a JSON source.

        Args:
            source: Path or identifier for the JSON source.
            **kwargs: Additional keyword arguments.

        Returns:
            A populated Recipe instance.
        """

    def save_data(self, destination: str | Path, data: Recipe, **kwargs: Any) -> None:
        """Save a Recipe instance to a JSON destination.

        Args:
            destination: Path where the JSON file should be written.
            data: The Recipe instance to save.
            **kwargs: Additional keyword arguments.
        """


def select_loader(file_extension: str) -> DataLoader[Any]:
    """Select and return an appropriate DataLoader instance based on file format.

    Args:
        file_extension: The extension or format identifier (e.g., '.csv', '.json').

    Returns:
        An instance of a DataLoader subclass matching the format.

    Raises:
        ValueError: If the format is unsupported.
    """
    ext = file_extension.strip().lower()
    if ext in (".csv", "csv"):
        return CSVDataLoader()
    elif ext in (".json", "json"):
        return JSONDataLoader()
    raise ValueError(f"Unsupported data format: {file_extension}")
