import os

from .src import create_app, deregister_on_exit


def run_data_access_gateway():
    app = create_app()
    try:
        app.run(host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=int(os.getenv('FLASK_RUN_PORT', '5020')))
    finally:
        deregister_on_exit(app)
