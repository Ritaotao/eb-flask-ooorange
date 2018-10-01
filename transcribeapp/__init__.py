from flask import Flask
from .config import Config, AWSConfig

application = Flask(__name__)
application.config.from_object(Config)

from transcribeapp import routes
