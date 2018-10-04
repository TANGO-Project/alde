#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Unit tests that checks ALDE Datamodel
#

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
