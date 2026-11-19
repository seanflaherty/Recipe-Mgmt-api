"""SQLAlchemy ORM models for the recipe management app."""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class RecipeModel(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # Relationships to child tables
    ingredients = relationship(
        "RecipeIngredientModel",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    instructions = relationship(
        "InstructionModel",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )


class RecipeIngredientModel(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="")
    dietary_tags = Column(String, default="")  # Stored as comma-separated or JSON

    recipe = relationship("RecipeModel", back_populates="ingredients")


class InstructionModel(Base):
    __tablename__ = "instructions"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    description = Column(String, nullable=False)
    equipment = Column(String, default="")
    prep_time = Column(Integer, default=0)
    include_in_prep_time = Column(Boolean, default=True)

    recipe = relationship("RecipeModel", back_populates="instructions")
