# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from model.base import db

class ExecutionScript(db.Model):
    """
    Object that represetns all the information for executing an
    application into a testbed by the ALDE
    """

    # SQLAlchemy mapping code
    __tablename__ = 'execution_scripts'
    id = db.Column(db.Integer, primary_key=True)
    command = db.Column(db.String)
    execution_type = db.Column(db.String)
    parameters = db.Column(db.String)

    def __init__(self, command, execution_type, parameters):
        """Initialize basic parameters of the class"""

        self.command = command
        self.execution_type = execution_type
        self.parameters = parameters

class Application(db.Model):
    """
    Object that represents all the information for an
    application that it needs to be build and maybe deploy by the
    Application Lifecycle Deployment Engine
    """

    # SQLAlchemy mapping code
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


    def __init__(self, name):
        """Initializes the basic parameters of the class"""

        self.name = name

