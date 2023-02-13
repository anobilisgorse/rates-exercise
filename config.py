import os

class Config(object):
    ENV = 'local'
    DB_HOST = 'localhost'
    DB_NAME = 'postgres'
    DB_USER = 'postgres'
    DB_PASSWORD = 'ratestask' # TODO: Move to environment variable?

class DockerConfig(Config):
    ENV = 'docker'
    DB_HOST = os.environ.get('DB_HOST')
    DB_PASSWORD = os.environ.get('DB_PASSWORD') 