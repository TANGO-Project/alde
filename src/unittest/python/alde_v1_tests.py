# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from flask import Flask
from flask_testing import TestCase
from model.base import db
from model.application import Application
import alde

class AldeTests(TestCase):
    """
    Test that verifies the REST API of Alde for its v1 version
    """

    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        """
        It initializes the application
        """

        app = alde.create_app_v1(self.SQLALCHEMY_DATABASE_URI, 5101)

        return app

    def setUp(self):
        """
        It creates the memory db
        """

        db.create_all()

        # We store some data in the db for the tests
        application_1 = Application("AppName_1", "Path_1")
        application_2 = Application("AppName_2", "Path_2")
        db.session.add(application_1)
        db.session.add(application_2)

        db.session.commit()

    def setDown(self):
        """
        Deletes everything in the memory db
        """

        db.session_remove()

    def test_application_rest_api(self):
        """
        It tests all supported REST methods for an Application works
        as expected.
        """

        response = self.client.get("/api/v1/applications")

        print(response.json)
