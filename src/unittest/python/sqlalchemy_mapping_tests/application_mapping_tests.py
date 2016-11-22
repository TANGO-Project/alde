# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from model.base import Base
from model.application import Application
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class ApplicationMappingTest(unittest.TestCase):
    """
    It verifies the SQL mapping done with SQLAlchemy libs
    """

    def setUp(self):
        """Does the initial setup of SQLAlchemy"""

        self.engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def test_crud_application(self):
        """It test basic CRUD operations of an Application Class"""

        # We verify that the object is not in the db after creating
        application = Application("AppName", "Path")
        self.assertIsNone(application.id)

        # We store the object in the db
        self.session.add(application)

        # We recover the application from the db
        application = self.session.query(Application).filter_by(name='AppName').first()
        self.assertIsNotNone(application.id)
        self.assertEquals("AppName", application.name)
        self.assertEquals("Path", application.path_to_code)


    def tearDown(self):
        """ It closes the session after each test """
        Base.metadata.drop_all(self.engine)
