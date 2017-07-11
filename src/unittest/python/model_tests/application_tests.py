# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from models import Application, ExecutionScript

class ApplicationTest(unittest.TestCase):
    """
    Unit tests for all the different classes in the model.application
    module
    """

    def test_initialization_application(self):
        """Test the initialization method of the class Application"""

        application = Application("name")
        self.assertEquals("name", application.name)

    def test_initialization_execution_script(self):
        """Test the initialization method of the class Execution Scripts"""

        execution_script = ExecutionScript("command", "type", "1 2 3")
        self.assertEquals("command", execution_script.command)
        self.assertEquals("type", execution_script.execution_type)
        self.assertEquals("1 2 3", execution_script.parameters)
