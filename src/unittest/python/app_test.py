# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
import app

class AppTests((unittest.TestCase):
    """
    Since App only loads the app... nothing to test hetegoregenous
    """

    def test_app(self):
        self.assertEquals('sqlite:////tmp/test.db', app.SQL_LITE_URL)
        self.assertEquals(5000, app.PORT)
