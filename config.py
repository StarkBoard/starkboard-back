import os

class Config:
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = os.getenv("SECRET_KEY", "")

class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True