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
from models import Executable

class ExecutableTest(unittest.TestCase):
	"""
	Unit tests for the class Executable
	"""

	def test_initialization_executable(self):
		"""Test the initialization of the object"""

		executable = Executable()
		executable.source_code_file = "source"
		executable.compilation_script = "script"
		executable.compilation_type = "type"
		executable.singularity_app_folder = "app_folder"
		executable.singularity_image_file = "image.img"
		executable.status = "NOT_COMPILED"

		self.assertEquals("source", executable.source_code_file)
		self.assertEquals("script", executable.compilation_script)
		self.assertEquals("type", executable.compilation_type)
		self.assertEquals("NOT_COMPILED", executable.status)
		self.assertEquals("app_folder", executable.singularity_app_folder)
		self.assertEquals("image.img", executable.singularity_image_file)

