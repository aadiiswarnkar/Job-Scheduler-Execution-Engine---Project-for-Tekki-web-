#In this file, we set up the Flask application for the job scheduler, configure Swagger for API documentation, initialize the database, and register the job controller blueprint. It also starts the Flask server.

from flask import Flask
from flasgger import Swagger

from app.controller.jobs_controller import jobs_bp
from app.db.session import init_db

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Job Scheduler & Execution Engine API",
        "description": "Backend API for job scheduling and execution",
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http"],
}

Swagger(app, config=swagger_config, template=swagger_template)

init_db()
app.register_blueprint(jobs_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
