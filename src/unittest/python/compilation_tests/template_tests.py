# This file verifies that we update correctly the templates
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
import os
import compilation.template as template

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
			print("Test test test file...", file=text_file)
			print("some text{#FOLDER_LOCATION#}...", file=text_file)
			print("Test test test file...", file=text_file)
			print("Test {#APP_FOLDER#}test {#FOLDER_LOCATION#}...", file=text_file)
			print("Test test test file...", file=text_file)
			print("{#APP_FOLDER#} test {#BUILD_COMMAND#} file...", file=text_file)
			print("end of file", file=text_file)


		destination_template = template.update_template("test_update_template_variables.txt",
														"gcc -x1",
														"/home/pepito",
														"application")

		# We read all the lines
		lines = [line.rstrip('\n') for line in open(destination_template)]

		self.assertEquals("Test test test file...", line[0])
		self.assertEquals("some text/home/pepito...", line[1])
		self.assertEquals("Test test test file...", line[2])
		self.assertEquals("Test applicationtest /home/pepito...", line[3])
		self.assertEquals("Test test test file...", line[4])
		self.assertEquals("application test gcc -x1 file...", line[5])
		self.assertEquals("end of file", line[6])

		# We clean after the test
		os.remove("test_update_template_variables.txt")