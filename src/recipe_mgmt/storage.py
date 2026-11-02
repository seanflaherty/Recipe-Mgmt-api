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
        """Load a single Recipe from a structured CSV file.

        Args:
            source: Path to the CSV file.
            **kwargs: Additional keyword arguments.

        Returns:
            A populated Recipe instance.
        """
        filepath = Path(source)
        name = filepath.stem
        name = name.replace("_", " ").title()
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
        filepath = Path(destination)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "type",
            "ingredient_name",
            "dietary_tags",
            "quantity",
            "unit",
            "instruction",
            "prep_time",
            "equipment",
            "include_in_prep_time",
        ]

        with filepath.open(mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Write each recipe ingredient row
            for ri in data.recipe_ingredients:
                tags_str = ";".join(tag.value for tag in ri.ingredient.dietary_tags)
                writer.writerow({
                    "type": "ingredient",
                    "ingredient_name": ri.ingredient.name,
                    "dietary_tags": tags_str,
                    "quantity": ri.quantity,
                    "unit": ri.unit,
                    "instruction": "",
                    "prep_time": "",
                    "equipment": "",
                    "include_in_prep_time": "",
                })

            # Write each instruction row
            for instr in data.instructions:
                eq_str = ";".join(instr.equipment)
                writer.writerow({
                    "type": "instruction",
                    "ingredient_name": "",
                    "dietary_tags": "",
                    "quantity": "",
                    "unit": "",
                    "instruction": instr.description,
                    "prep_time": instr.prep_time,
                    "equipment": eq_str,
                    "include_in_prep_time": str(instr.include_in_prep_time),
                })



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
        raise NotImplementedError("JSON loading is not yet implemented.")

    def save_data(self, destination: str | Path, data: Recipe, **kwargs: Any) -> None:
        """Save a Recipe instance to a structured CSV destination.

        Args:
            destination: Path where the CSV file should be written.
            data: The Recipe instance or dictionary-backed object to save.
            **kwargs: Additional keyword arguments.
        """
        filepath = Path(destination)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "type",
            "ingredient_name",
            "dietary_tags",
            "quantity",
            "unit",
            "instruction",
            "prep_time",
            "equipment",
            "include_in_prep_time",
        ]

        with filepath.open(mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Handle recipe ingredients (whether objects or raw dictionaries)
            recipe_ingredients = getattr(data, "recipe_ingredients", [])
            for ri in recipe_ingredients:
                if isinstance(ri, dict):
                    ing_data = ri.get("ingredient", {})
                    if isinstance(ing_data, dict):
                        ing_name = ing_data.get("name", "")
                        raw_tags = ing_data.get("dietary_tags", [])
                        tags_str = ";".join(
                            t.get("name", "") if isinstance(t, dict) else str(t)
                            for t in raw_tags
                        )
                    else:
                        ing_name = str(ing_data)
                        tags_str = ""
                    quantity = ri.get("quantity", 0)
                    unit = ri.get("unit", "")
                else:
                    tags_str = ";".join(tag.value for tag in ri.ingredient.dietary_tags)
                    ing_name = ri.ingredient.name
                    quantity = ri.quantity
                    unit = ri.unit

                writer.writerow({
                    "type": "ingredient",
                    "ingredient_name": ing_name,
                    "dietary_tags": tags_str,
                    "quantity": quantity,
                    "unit": unit,
                    "instruction": "",
                    "prep_time": "",
                    "equipment": "",
                    "include_in_prep_time": "",
                })

            # Handle instructions (whether objects or raw dictionaries)
            instructions = getattr(data, "instructions", [])
            for instr in instructions:
                if isinstance(instr, dict):
                    desc = instr.get("description", "")
                    prep_t = instr.get("prep_time", 0)
                    eq_list = instr.get("equipment", [])
                    eq_str = ";".join(eq_list) if isinstance(eq_list, list) else str(eq_list)
                    inc_prep = str(instr.get("include_in_prep_time", True))
                else:
                    desc = instr.description
                    prep_t = instr.prep_time
                    eq_str = ";".join(instr.equipment)
                    inc_prep = str(instr.include_in_prep_time)

                writer.writerow({
                    "type": "instruction",
                    "ingredient_name": "",
                    "dietary_tags": "",
                    "quantity": "",
                    "unit": "",
                    "instruction": desc,
                    "prep_time": prep_t,
                    "equipment": eq_str,
                    "include_in_prep_time": inc_prep,
                })

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
