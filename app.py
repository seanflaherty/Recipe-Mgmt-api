"""
Recipe Management Application Entry Point.

This module initializes and configures the Flask application using Connexion
to map OpenAPI 3.0 specifications to Python handler functions. It exposes
the WSGI application interface for production deployment.
"""
from flask import Flask
import connexion

def create_app() -> Flask:
    """
    Application factory that initializes the Connexion and Flask framework instances.

    This function configures the routing engine by loading the OpenAPI specification
    file, registers foundational fallback utility routes (like the root health check),
    and extracts the underlying WSGI Flask instance required by production servers.

    Returns:
        Flask: A fully configured and initialized Flask application instance ready
               to handle incoming HTTP requests.
    """

    # Initialize Connexion
    connexion_app = connexion.FlaskApp(__name__, specification_dir='./openapi/')

    # Add the OpenAPI specification file
    connexion_app.add_api('recipe_mgmt.openapi.yaml')

    # Get the underlying Flask instance
    flask_app = connexion_app.app

    # Define the root route on the active Flask instance
    @flask_app.route("/")
    def home():
        return "Hello recipes! (root)"

    return flask_app

# Expose the application factory result for the WSGI production server
app = create_app()
