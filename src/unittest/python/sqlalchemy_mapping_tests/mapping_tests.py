# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from model.base import Base
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class MappingTest(unittest.TestCase):
    """
    Common methods for all mapping test code
    """

    def setUp(self):
        """Does the initial setup of SQLAlchemy"""

        self.engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def tearDown(self):
        """ It closes the session after each test """
        Base.metadata.drop_all(self.engine)
