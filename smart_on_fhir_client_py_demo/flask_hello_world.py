# AUTOGENERATED! DO NOT EDIT! File to edit: 50_flask_hello_world.ipynb (unless otherwise specified).

__all__ = ['create_app']

# Cell
from flask import Flask

# Cell
def create_app(test_config=None):
    "Create and configure an instance of the Flask application."
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev"
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    @app.route("/hello")
    def hello_world():
        return f"Hello, World!"

    @app.route("/hello/<human_name>")
    def hello(human_name):
        return f"Hello, {human_name}!"

    app.add_url_rule("/", endpoint="hello_world")

    return app

# Cell
try: from nbdev.imports import IN_NOTEBOOK
except: IN_NOTEBOOK = False
if __name__ == "__main__" and not IN_NOTEBOOK:
    create_app().run(debug=True, port=8000)