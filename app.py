from flask import Flask
import connexion

app = Flask(__name__)

def create_app() -> Flask:
    app = connexion.FlaskApp(__name__, specification_dir='./openapi/')
    app.add_api('recipe_mgmt.openapi.yaml')
    return app.app

@app.route("/")
def home():
    return "Hello receipes! (root)"