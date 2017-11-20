# This file verifies that we update correctly the templates
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
import unittest.mock as mock
import os
import compilation.template as template
from uuid import UUID
from testfixtures import LogCapture

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

		l = LogCapture()

		template.upload_folder="."

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

		self.assertEquals("Test test test file...", lines[0])
		self.assertEquals("some text/home/pepito...", lines[1])
		self.assertEquals("Test test test file...", lines[2])
		self.assertEquals("Test applicationtest /home/pepito...", lines[3])
		self.assertEquals("Test test test file...", lines[4])
		self.assertEquals("application test gcc -x1 file...", lines[5])
		self.assertEquals("end of file", lines[6])

		# We clean after the test
		os.remove("test_update_template_variables.txt")
		os.remove(destination_template)

		# We verify the name follows the righ nomenclature
		filename = os.path.basename(destination_template)
		log_string = 'Template generated on: ./' + filename
		filename = filename[:-4]

		try:
			val = UUID(filename, version=4)
		except ValueError:
			self.fail("Filname is not uuid4 complaint: " + filename)



		# Checking that we are logging the correct messages
		l.check(
			('root', 'INFO', 'Creating singulartiy template using file: test_update_template_variables.txt'),
			('root', 'INFO', log_string)
			)
		l.uninstall()