import os

from .src import create_app


def run_gateway():
    app = create_app()
    app.run(host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=int(os.getenv('FLASK_RUN_PORT', '5001')))
