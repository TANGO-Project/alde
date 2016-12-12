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

class MappingTest(TestCase):
     """
     Common methods for all mapping test code
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
         db.app=app
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
