# 🍳 Recipe Management API

A full-stack Recipe Management web application and REST API built with **FastAPI**, **SQLAlchemy**, **Tailwind CSS**, **HTMX**, and **Vanilla JavaScript**. It supports relational database persistence (SQLite for local development and PostgreSQL for production) alongside an interactive single-page dashboard with full CRUD (Create, Read, Update, Delete) capabilities and Swagger API documentation.

---

## 🏗️ Architecture & Design

The project separates core domain logic, relational database models, API routing, and decoupled static frontend assets:

* **Domain Models (`components.py`, `recipe.py`, `recipe_book.py`):** Strongly-typed Python classes representing recipes, ingredients, dietary tags, instructions, and search/filtering logic.
* **Database Layer (`database.py`, `models.py`):** SQLAlchemy ORM configuration and relational models (`RecipeModel`, `RecipeIngredientModel`, `InstructionModel`) with cascading deletes (`cascade="all, delete-orphan"`), automatic table initialization, and session dependency injection.
* **API & Static Routing (`main.py`):** FastAPI application serving RESTful JSON/HTML endpoints, Pydantic request validation, interactive Swagger UI (`/ui`), and static assets mounted at `/static`.
* **Frontend Dashboard (`static/index.html`, `static/app.js`):** Responsive two-column dashboard styled with Tailwind CSS and powered by HTMX and decoupled JavaScript (`app.js`):
  * Dynamic multi-row ingredient and instruction builders.
  * Interactive recipe detail modal with in-app **Edit** (pre-filling the main form) and **Delete** (with confirmation) actions.
  * Dismissible inline status notifications with auto-fade for success messages and persistent alerts for errors.

---

## 📁 Project Structure

```text
recipe-mgmt-api/
├── src/
│   └── recipe_mgmt/
│       ├── recipes/            # Legacy CSV persistence directory
│       ├── __init__.py
│       ├── components.py       # Ingredients, DietaryTags, and domain components
│       ├── database.py         # SQLAlchemy engine, session, and DATABASE_URL setup
│       ├── main.py             # FastAPI app, CRUD endpoints, and static file mount
│       ├── models.py           # SQLAlchemy ORM models and cascading relationships
│       ├── recipe.py           # Core Recipe and Instruction domain classes
│       ├── recipe_book.py      # Collection manager & search criteria logic
│       └── storage.py          # Abstract loaders & CSV factory pattern
├── static/
│   ├── app.js                  # Decoupled frontend state, modal, CRUD, and toast logic
│   └── index.html              # Web dashboard (Tailwind CSS, HTMX, & modal UI)
├── pyproject.toml              # Project dependencies and metadata
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
* Python 3.11+
* A `.env` file in the project root defining `DATABASE_URL` (e.g., `sqlite:///./recipes.db` for local development)
* [Poetry](https://python-poetry.org/) for dependency management

### Installation & Setup

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd recipe-mgmt-api
   ```

2. **Install dependencies using Poetry:**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```bash
   DATABASE_URL=sqlite:///./recipes.db
   ```

---

## 🏃 Running the Application

Start the Uvicorn ASGI server:

```bash
uvicorn src.recipe_mgmt.main:app --reload --port 8000
```

* **Web Dashboard:** Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** to create, view, edit, and delete recipes interactively.
* **Interactive Swagger UI:** Open **[http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui)** to test API endpoints directly.
* **OpenAPI Specification:** Accessible at `http://127.0.0.1:8000/openapi.json`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/` | Serves the static `index.html` Recipe Management Dashboard. |
| **GET** | `/recipes-db` | Retrieves recipes from the database (supports optional `?name=` filtering) and returns formatted HTML items with embedded recipe JSON (including `id`) for the UI. |
| **POST** | `/recipes` | Validates and saves a new recipe, its ingredients, and its instructions to the database. |
| **PUT** | `/recipes/{id}` | Updates an existing recipe's name, ingredients, and instructions by primary key `id`. |
| **DELETE** | `/recipes/{id}` | Removes a recipe and its associated ingredients/instructions by primary key `id`. |

---

## 🧪 Example Request Payload (`POST /recipes` & `PUT /recipes/{id}`)

```json
{
  "name": "Homemade Bread",
  "recipe_ingredients": [
    {
      "ingredient": {
        "name": "Flour",
        "dietary_tags": ["VEGAN", "GLUTEN"]
      },
      "quantity": 3.0,
      "unit": "cups"
    }
  ],
  "instructions": [
    {
      "description": "Mix ingredients in a bowl.",
      "prep_time": 10,
      "equipment": ["mixing bowl"],
      "include_in_prep_time": true
    }
  ]
}
```

---

## ☁️ Deployment (Render)

The application is configured for deployment on Render using PostgreSQL via `DATABASE_URL`:

* **Build Command:** `pip install -e .`
* **Start Command:** `uvicorn src.recipe_mgmt.main:app --host 0.0.0.0 --port $PORT`

---

## 🛠️ Built With

* **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast Python web framework
* **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit and ORM
* **[Tailwind CSS & HTMX](https://tailwindcss.com/)** - Frontend styling and dynamic HTML updates
* **[Poetry](https://python-poetry.org/)** - Dependency management and packaging
* **[Uvicorn](https://www.uvicorn.org/)** - Lightning-fast ASGI server implementation