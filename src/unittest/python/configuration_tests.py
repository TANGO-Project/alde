# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
import configparser

class ConfigurationTest(unittest.TestCase):
    """
    Set of examples to understand how configuration works
    """

    def test_read(self):
        """ Checks it is possible to read the configuration """
        config = configparser.ConfigParser()
        config.sections()
        config.read('alde_configuration.ini')
        self.assertTrue('DEFAULT' in config)
        self.assertEquals(config['DEFAULT']['SQL_LITE_URL'], 'sqlite:////tmp/test.db')
        self.assertEquals(config['DEFAULT']['PORT'], '5000')
