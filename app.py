import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
from starkboard.routes import app_routes

app = Flask(__name__)
CORS(app)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

app.register_blueprint(app_routes)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)