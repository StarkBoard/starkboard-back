import os
from flask import Flask
from dotenv import load_dotenv
load_dotenv()
from starkboard.routes import app_routes

app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

app.register_blueprint(app_routes)


if __name__ == '__main__':
    import starkboard.routes

    app.run()