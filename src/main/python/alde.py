# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import flask
import flask_restless
from model.base import db
from model.application import Application
from model.models import Testbed

url_prefix_v1='/api/v1'

def create_app_v1(sql_db_url, port):
    """
    It creates the Flask REST app service
    """

    # We create the Flask App
    app = flask.Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = sql_db_url
    app.config['LIVESERVER_PORT'] = port
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    db.init_app(app)
    db.app=app

    # Create the Flask-Restless API manager.
    manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

    # Create the REST methods for an Application
    manager.create_api(Application,
                       methods=['GET', 'POST', 'DELETE'],
                       url_prefix=url_prefix_v1)

    # Create the REST methods for a Testbed
    manager.create_api(Testbed,
                       methods=['GET', 'POST', 'PUT', 'DELETE'],
                       url_prefix=url_prefix_v1)

    return app
