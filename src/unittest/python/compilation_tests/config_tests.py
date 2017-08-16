# Unit tests to verify that it is possible to read the configuration tests
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

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

		config.COMPILATION_CONFIG_FILE = "./src/main/python/compilation_config.json"

		configuration = config.find_compilation_config('SINGULARITY:PM')
		self.assertEquals(configuration['connection_type'], 'SSH')
		self.assertEquals(configuration['connection_url'], 'ubuntu@localhost:2222')
		self.assertEquals(configuration['singularity_template'], 'templates/compilation/singularity_pm.def')

		configuration = config.find_compilation_config('asda')
		self.assertIsNone(configuration)