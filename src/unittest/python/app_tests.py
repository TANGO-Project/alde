# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from app import load_config

class AppTests(unittest.TestCase):
    """
    Unit tests for the methods of the main app
    """

    def test_load_config(self):
        """ Test that verifies the app loads the right config """

        conf = load_config()

        self.assertEquals('sqlite:////tmp/test.db', conf['SQL_LITE_URL'])
        self.assertEquals('5000', conf['PORT'])
        self.assertEquals('/tmp', conf['APP_UPLOAD_FOLDER'])
        self.assertEquals('/tmp', conf['APP_PROFILE_FOLDER'])
        self.assertEquals(["RIGID", "MOULDABLE", "CHECKPOINTABLE", "MALLEABLE"], conf['APP_TYPES'])
