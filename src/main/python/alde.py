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
from model.models import Testbed, Node

url_prefix_v1='/api/v1'
accepted_message = { 'create' : True, 'reason' : ''}
testbed_not_configured_message = { 'create' : False, 'reason' : 'Testbed is configured to automatically retrieve information of nodes'}
no_testbed = 'Testbed does not exist'

def _testbed_creation_node(testbed):
    """
    Internal function to check if the testbed exists and allow or not the
    creation of a node
    """

    if testbed == None:
        return { 'create' : False, 'reason' : no_testbed }
    elif testbed.on_line :
        return testbed_not_configured_message
    else:
        return accepted_message

def can_create_the_node(node=None, testbed_id=-1, testbed=None):
    """
    It checks if it is possible to add a Node.
    It is necessary to check first if the testbed exits in the db
    Or if the is due to the creation of the own testbed
    Or if the node is independent and not associated to a testbed.
    """

    if testbed_id == -1 and testbed == None :
        if node.testbed_id == None :
            return accepted_message
        else:
            testbed = db.session.query(Testbed).filter_by(id=node.testbed_id).first()
            return _testbed_creation_node(testbed)

    elif testbed_id != -1 :
        testbed = db.session.query(Testbed).filter_by(id=testbed_id).first()
        return _testbed_creation_node(testbed)

    else:
        if testbed.on_line :
            return testbed_not_configured_message
        else:
            return accepted_message

def put_testbed_preprocessor(instance_id=None, data=None, **kw):
    """
    It is going to check if the testbed allows the creation of nodes
    """

    if instance_id != None :

        if 'nodes' in data :
            create =  can_create_the_node(testbed_id=instance_id)

            if not create['create'] and create['reason'] != no_testbed :
                raise flask_restless.ProcessingException(
                                                description=create['reason'],
                                                code=405)



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
                       preprocessors={
                            'PUT_SINGLE': [put_testbed_preprocessor]
                            },
                       url_prefix=url_prefix_v1)

    # Create teh REST methods for a Node
    manager.create_api(Node,
                       methods=['GET', 'POST', 'PUT', 'DELETE'],
                       url_prefix=url_prefix_v1)

    return app
