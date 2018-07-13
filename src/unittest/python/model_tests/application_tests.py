# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from models import Application, ExecutionConfiguration

class ApplicationTest(unittest.TestCase):
    """
    Unit tests for all the different classes in the model.application
    module
    """

    def test_initialization_application(self):
        """Test the initialization method of the class Application"""

        application = Application()
        application.name = "name"
        self.assertEquals("name", application.name)
        application.application_type = "XXX"
        self.assertEquals("XXX", application.application_type)

    def test_initialization_execution_configuration(self):
        """Test the initialization method of the class Execution Scripts"""

        execution_configuration = ExecutionConfiguration()
        execution_configuration.execution_type = "type"
        self.assertEquals("type", execution_configuration.execution_type)
