# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from model.application import Application, Build, Execution

class ApplicationTest(unittest.TestCase):
    """
    Unit tests for all the different classes in the model.application
    module
    """

    def test_initialization_execution(self):
        """Test the initalization method of the class Execution"""

        execution = Execution("ls", "la")
        self.assertEquals("ls", execution.command)
        self.assertEquals("la", execution.params)

    def test_initliazation_build(self):
        """Test the initialization method of the class Build"""

        build = Build("cc", "X")
        self.assertEquals("cc", build.script)
        self.assertEquals("X", build.params)

    def test_initialization_application(self):
        """Test the initialization method of the class Application"""

        application = Application("name", "c:")
        self.assertEquals("name", application.name)
        self.assertEquals("c:", application.path_to_code)
        self.assertEquals("", application.build.script)
        self.assertEquals("", application.build.params)
        self.assertEquals([], application.package)
        self.assertEquals([], application.executable)
        self.assertEquals("", application.execution.command)
        self.assertEquals("", application.execution.params)
