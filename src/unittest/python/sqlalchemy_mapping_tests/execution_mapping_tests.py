# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Execution

class ExecutionMappingTest(MappingTest):
	"""
	Series of test to validate the correct mapping to the class
	Execution to be stored into an SQL relational db
	"""

	def test_crud_execution(self):
		"""It test basic CRUD operations of an Execution class"""

		# We verify that the object is not in the db after creating it

		execution = Execution("command", "execution_type", "parameters", "status")
		self.assertIsNone(execution.id)

		# We store the object in the db
		db.session.add(execution)

		# We recover the execution from the db
		execution = db.session.query(Execution).filter_by(command="command").first()
		self.assertIsNotNone(execution.id)
		self.assertEquals("command", execution.command)
		self.assertEquals("execution_type", execution.execution_type)
		self.assertEquals("parameters", execution.parameters)
		self.assertEquals("status", execution.status)

		# We check that we can update the execution
		execution.execution_type = "X"
		db.session.commit()
		execution_2 = db.session.query(Execution).filter_by(command="command").first()
		self.assertEquals(execution.id, execution_2.id)
		self.assertEquals("X", execution.execution_type)

		# We check the delation
		db.session.delete(execution_2)
		count = db.session.query(Execution).filter_by(command="command").count()
		self.assertEquals(0, count)