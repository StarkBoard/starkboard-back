import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "")

class ProductionConfig(Config):
    TESTING = False
    DEBUG = False
    DEVELOPMENT = False

class DevelopmentConfig(Config):
    ENV='development'
    TESTING = True
    DEBUG = True
    DEVELOPMENT = True