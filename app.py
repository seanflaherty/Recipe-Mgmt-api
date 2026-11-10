"""
Recipe Management Application Entry Point.

This module initializes and configures the Flask application using Connexion
to map OpenAPI 3.0 specifications to Python handler functions. It exposes
the WSGI application interface for production deployment.
"""
import os
import sys
import connexion
from connexion.options import SwaggerUIOptions

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_dir, 'src'))

def create_app():
    """
    Application factory that initializes the Connexion and Flask framework instances.

    This function configures the routing engine by loading the OpenAPI specification
    file, registers foundational fallback utility routes (like the root health check),
    and extracts the underlying WSGI Flask instance required by production servers.

    Returns:
        Flask: A fully configured and initialized Flask application instance ready
               to handle incoming HTTP requests.
    """
    spec_dir = os.path.join(base_dir, 'src', 'recipe_mgmt')

    # Configure Swagger UI
    swagger_options = SwaggerUIOptions(swagger_ui=True, swagger_ui_path="/ui")

    # Initialize Connexion
    connexion_app = connexion.FlaskApp(
        __name__,
        specification_dir=spec_dir,
        swagger_ui_options=swagger_options
    )

    # Add the OpenAPI specification file
    connexion_app.add_api('recipe_mgmt.openapi.yaml')

   # Define fallback routes directly on the connexion_app wrapper
    @connexion_app.route("/")
    def home():
        return "Hello recipes! (root)"

    return connexion_app

# Expose the application factory result for the WSGI production server
app = create_app()
