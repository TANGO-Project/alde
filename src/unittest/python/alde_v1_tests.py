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
import json

class AldeV1Tests(TestCase):
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

        # GET
        response = self.client.get("/api/v1/applications")

        # We verify the respongse to the GET
        self.assertEquals(200, response.status_code)
        applications = response.json['objects']
        self.assertEquals(2, len(applications))
        application = applications[0]
        self.assertEquals(1, application['id'])
        self.assertEquals('AppName_1', application['name'])
        self.assertEquals('Path_1', application['path_to_code'])
        application = applications[1]
        self.assertEquals(2, application['id'])
        self.assertEquals('AppName_2', application['name'])
        self.assertEquals('Path_2', application['path_to_code'])

        # POST
        data={
                'name' : 'AppName_3',
                'path_to_code' : 'Path_3'
            }

        response = self.client.post('/api/v1/applications',
                                     data=json.dumps(data),
                                     content_type='application/json')

        self.assertEquals(201, response.status_code)
        self.assertEquals('AppName_3', response.json['name'])
        self.assertEquals('Path_3', response.json['path_to_code'])
        self.assertEquals(3, response.json['id'])
