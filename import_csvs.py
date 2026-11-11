"""One-time script to import flat recipe CSVs into the SQLAlchemy database."""

from pathlib import Path
import csv
from recipe_mgmt.database import SessionLocal, engine, Base
from recipe_mgmt.models import RecipeModel, RecipeIngredientModel, InstructionModel

# Ensure tables exist
Base.metadata.create_all(bind=engine)


def import_csv_recipes():
    db = SessionLocal()
    csv_dir = Path("src/recipe_mgmt/recipes")  # Adjust path to where your CSVs live

    # Find all CSV files in current dir or the recipes folder
    csv_files = list(Path(".").glob("*.csv")) + list(csv_dir.glob("*.csv"))

    # Deduplicate paths
    csv_files = list(set(csv_files))

    if not csv_files:
        print("No CSV files found!")
        db.close()
        return

    for file_path in csv_files:
        recipe_name = file_path.stem.replace("_", " ").title()

        # Check if already imported
        existing = db.query(RecipeModel).filter(RecipeModel.name == recipe_name).first()
        if existing:
            print(f"Skipping '{recipe_name}' (already in database)")
            continue

        print(f"Importing: {recipe_name} from {file_path.name}")
        db_recipe = RecipeModel(name=recipe_name)

        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_type = row.get("type", "").strip().lower()

                if row_type == "ingredient":
                    ing_name = row.get("ingredient_name", "").strip()
                    if ing_name and ing_name != "-":
                        try:
                            qty = float(row.get("quantity", 1.0) or 1.0)
                        except ValueError:
                            qty = 1.0
                        unit = row.get("unit", "").strip()
                        tags = row.get("dietary_tags", "").strip()

                        db_recipe.ingredients.append(
                            RecipeIngredientModel(
                                ingredient_name=ing_name,
                                quantity=qty,
                                unit=unit,
                                dietary_tags=tags,
                            )
                        )
                elif row_type == "instruction":
                    desc = row.get("instruction", "").strip()
                    if desc and desc != "-":
                        try:
                            prep_time = int(row.get("prep_time", 0) or 0)
                        except ValueError:
                            prep_time = 0
                        include_flag = (
                            row.get("include_in_prep_time", "True").strip().lower()
                            == "true"
                        )

                        db_recipe.instructions.append(
                            InstructionModel(
                                description=desc,
                                prep_time=prep_time,
                                include_in_prep_time=include_flag,
                            )
                        )

        db.add(db_recipe)
        db.commit()
        print(
            f"Successfully imported {recipe_name} with {len(db_recipe.ingredients)} ingredients and {len(db_recipe.instructions)} instructions."
        )

    db.close()


if __name__ == "__main__":
    import_csv_recipes()
