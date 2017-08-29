# This file verifies that we update correctly the templates
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
import os

class TemplateTests(unittest.TestCase):
	"""
	It verifies that the methods package that updates the template
	configuration works as expected
	"""

	def test_update_template_variables(self):
		"""
		It checks that we are able to update the following variables
		of a template:
		- {#FOLDER_LOCATION#}
		- {#APP_FOLDER#}
		- {#BUILD_COMMAND#}
		"""

		# We prepare the file that we are going to use for the tests
		with open("test_update_template_variables.txt", "w") as text_file:
			print(f"Purchase Amount", file=text_file)

		# We clean after the test
		os.remove("test_update_template_variables.txt")