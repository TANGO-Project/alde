# SQLAlchemy mapping tests for the class Executable
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Executable

class ExecutableMappingTest(MappingTest):
	"""
	Series of test to validate the correct mapping to the class
	Executable to be stored into an SQL relational db
	"""

	def test_crud_executable(self):
		"""It tests basis CRUD operations of an Executable Class"""

		# We verify that the object is not in the db after creating it
		executable = Executable("source", "script", "type")
		self.assertIsNone(executable.id)

		# We store the object in the db
		db.session.add(executable)
		db.session.commit()

		# We recover the executable form the db
		executable = db.session.query(Executable).filter_by(id=executable.id).first()
		self.assertEquals("source", executable.source_code_file)

		# We check that we can update the Executable
		executable.executable_file = 'pepito'
		executable.singularity_app_folder = "app_folder"
		db.session.commit()
		executable = db.session.query(Executable).filter_by(id=executable.id).first()
		self.assertEquals('pepito', executable.executable_file)
		self.assertEquals('app_folder', executable.singularity_app_folder)

		# We check that we can delete the Executable
		db.session.delete(executable)
		db.session.commit()
		count = db.session.query(Executable).count()
		self.assertEquals(0, count)