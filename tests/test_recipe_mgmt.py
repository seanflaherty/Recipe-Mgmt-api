<<<<<<< HEAD:tests/recipe_mgmt_tests.py
from recipe_mgmt.app import create_app
=======
# from src.app import create_app
from app import create_app
>>>>>>> 7f18d688c162b3f215afc2917a0cf1fd1117967d:tests/test_recipe_mgmt.py


def test_can_create_app():
    app = create_app()
    assert app is not None