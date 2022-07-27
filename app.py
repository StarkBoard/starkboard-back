import os
from flask import Flask

app = Flask(__name__)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
print(env_config)

app.config.from_object(env_config)

import starkboard.routes


if __name__ == '__main__':
    app.run()