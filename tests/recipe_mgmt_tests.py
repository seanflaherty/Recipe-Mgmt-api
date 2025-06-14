from recipe_mgmt.app import create_app


def test_can_create_app():
    app = create_app()
    assert app is not None