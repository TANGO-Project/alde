#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.gnu.org/licenses/agpl-3.0.txt
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
from models import Execution

class ExecutionTests(unittest.TestCase):
	"""
	Unit test for the class Execution inside the models package
	"""

	def test_initialization_execution(self):
		"""Test the initializacion method of the class Execution"""

		execution = Execution()
		execution.execution_type = "execution_type"
		execution.status = "status"

		self.assertEquals("execution_type", execution.execution_type)
		self.assertEquals("status", execution.status)