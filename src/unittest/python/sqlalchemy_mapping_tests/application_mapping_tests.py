# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from flask import Flask
from flask_testing import TestCase
from model.application import Application, db

class ApplicationMappingTest(TestCase):
    """
    Series of test to validate the correct mapping to the class
    Application to be stored into an SQL relational db
    """

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        """
        It initializes flask_testing
        """

        app = Flask(__name__)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        db.init_app(app)
        return app

    def setUp(self):
        """
        It creates the memory db
        """

        db.create_all()

    def setDown(self):
        """
        Deletes everything in the memory db
        """

        db.session_remove()
        db.drop_all()

    def test_crud_application(self):
        """It test basic CRUD operations of an Application Class"""

        # We verify that the object is not in the db after creating
        application = Application("AppName", "Path")
        self.assertIsNone(application.id)

        # We store the object in the db
        db.session.add(application)

        # We recover the application from the db
        application = db.session.query(Application).filter_by(name='AppName').first()
        self.assertIsNotNone(application.id)
        self.assertEquals("AppName", application.name)
        self.assertEquals("Path", application.path_to_code)

        # We check that we can update the application
        application.name = 'pepito'
        db.session.commit()
        application_2 = db.session.query(Application).filter_by(name='pepito').first()
        self.assertEquals(application.id, application_2.id)
        self.assertEquals("pepito", application.name)
        self.assertEquals("Path", application.path_to_code)

        # We check the deletion
        db.session.delete(application_2)
        count = db.session.query(Application).filter_by(name='pepito').count()
        self.assertEquals(0, count)
