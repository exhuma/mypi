"""
Main web application code.
"""
from __future__ import print_function
import logging

from flask import Flask

LOG = logging.getLogger(__name__)
APP = Flask(__name__)


def create_app(sessionmaker, config):
    app = Flask(__name__)
    app._mypi_conf = config
    app._sessionmaker = sessionmaker

    from mypi.views.core import CORE
    app.register_blueprint(CORE)
    return app


if __name__ == "__main__":
    print(">>> Running DEVELOPMENT server!")
    from config_resolver import Config
    APP = create_app(Config('exhuma', 'mypi'))
    APP.run(host='0.0.0.0', debug=True)
