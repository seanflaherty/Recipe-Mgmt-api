# 🍳 Recipe Management API

A modular, persistent Recipe Management API built with Python, FastAPI/Connexion 3.x, Pydantic, and Poetry. This application implements clean architectural layers (Separation of Concerns), domain-driven design, and structured CSV file persistence.

---

## 🏗️ Architecture & Design

The project follows a strict separation of concerns, decoupling core domain models, business logic routing, API contract definitions, and storage handlers:

* **Domain Models (`components.py`, `recipe.py`):** Strongly-typed Python classes representing recipes, ingredients, quantities, dietary tags (e.g., `GLUTEN_FREE`, `NUT_FREE`), and instructions.
* **Storage Layer (`storage.py`):** Features an Abstract Base Class (`DataLoader`) and a Factory Pattern (`select_loader`) supporting structured multi-row CSV persistence and extensibility for other formats like JSON.
* **API Contract & Routing (`recipe_mgmt.openapi.yaml` & `main.py`):** Powered by Connexion 3.x and FastAPI/Flask ASGI layers, automatically validating incoming requests against the OpenAPI specification and exposing an interactive Swagger UI.

---

## 📁 Project Structure

```text
recipe-mgmt-api/
├── src/
│   └── recipe_mgmt/
│       ├── recipes/            # Directory for persisted recipe CSV files
│       ├── __init__.py
│       ├── components.py       # Ingredients, DietaryTags, and Repositories
│       ├── main.py             # API route handlers & Connexion app entrypoint
│       ├── recipe.py           # Core Recipe and Instruction models
│       ├── recipe_book.py      # Collection manager & search criteria logic
│       ├── recipe_mgmt.openapi.yaml # OpenAPI 3.0 API Specification
│       └── storage.py          # Abstract loaders & CSV factory pattern
├── pyproject.toml              # Poetry dependencies and project metadata
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
* Python 3.11+
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

---

## 🏃 Running the Application

Start the Uvicorn ASGI server using Poetry:

```bash
poetry run uvicorn recipe_mgmt.main:application --reload --port 8000
```

* **Interactive Swagger UI:** Open your browser and navigate to **[http://127.0.0.1:8000/ui/](http://127.0.0.1:8000/ui/)** to test endpoints interactively.
* **OpenAPI Specification:** Accessible at `http://127.0.0.1:8000/openapi.json` (or via your YAML contract).

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/recipes` | Retrieve all recipes or filter by name, ingredient, dietary tag, or max prep time. |
| **POST** | `/recipes` | Add a new recipe to the collection and automatically persist it as a structured CSV file in `src/recipe_mgmt/recipes/`. |
| **DELETE** | `/recipes/{name}` | Remove a recipe by name from the active recipe book. |

---

## 🧪 Example Request Payload (`POST /recipes`)

```json
{
  "name": "Gluten-Free Salad",
  "recipe_ingredients": [
    {
      "ingredient": {
        "name": "Lettuce",
        "dietary_tags": ["GLUTEN_FREE"]
      },
      "quantity": 1,
      "unit": "head"
    }
  ],
  "instructions": [
    {
      "description": "Wash greens thoroughly and chop.",
      "prep_time": 5,
      "equipment": ["Knife", "Cutting Board"],
      "include_in_prep_time": true
    }
  ]
}
```

---

## 🛠️ Built With

* **[Connexion 3.x](https://connexion.readthedocs.io/)** - OpenAPI-first framework for Python
* **[Uvicorn](https://www.uvicorn.org/)** - Lightning-fast ASGI server implementation
* **[Poetry](https://python-poetry.org/)** - Dependency management and packaging