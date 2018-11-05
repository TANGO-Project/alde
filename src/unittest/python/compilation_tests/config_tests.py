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
# unit tests for the loading of the config configuration for compilation
#

import unittest
import compilation.config as config

class ConfigTests(unittest.TestCase):
	"""
	Verifies the correct work all the functions inside compilation.config 
	module, responsible of parsing all json internal inventory infomration
	to complement the GPU and other hardware infomration of components
	in nodes used by ALDE
	"""

	def test_find_compilation_config(self):
		"""
		This tests verifies that we can find the right configuration compilation
		from a json-list stored file
		"""

		config.COMPILATION_CONFIG_FILE = "compilation_config.json"

		configuration = config.find_compilation_config('SINGULARITY:PM')
		self.assertEquals(configuration['connection_type'], 'SSH')
		self.assertEquals(configuration['connection_url'], 'ubuntu@localhost:2222')
		self.assertEquals(configuration['singularity_template'], 'templates/compilation/singularity_pm.def')

		configuration = config.find_compilation_config('asda')
		self.assertIsNone(configuration)