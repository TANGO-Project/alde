# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Execution, Node

class ExecutionMappingTest(MappingTest):
	"""
	Series of test to validate the correct mapping to the class
	Execution to be stored into an SQL relational db
	"""

	def test_crud_execution(self):
		"""It test basic CRUD operations of an Execution class"""

		# We verify that the object is not in the db after creating it

		execution = Execution()
		execution.execution_type = "execution_type"
		execution.status = "status"
		self.assertIsNone(execution.id)

		# We store the object in the db
		db.session.add(execution)

		# We recover the execution from the db
		execution = db.session.query(Execution).filter_by(execution_type="execution_type").first()
		self.assertIsNotNone(execution.id)
		self.assertEquals("execution_type", execution.execution_type)
		self.assertEquals("status", execution.status)

		# We check that we can update the execution
		execution.execution_type = "X"
		db.session.commit()
		execution_2 = db.session.query(Execution).filter_by(execution_type="X").first()
		self.assertEquals(execution.id, execution_2.id)
		self.assertEquals("X", execution.execution_type)

		# We check the delation
		db.session.delete(execution_2)
		count = db.session.query(Execution).filter_by(execution_type="X").count()
		self.assertEquals(0, count)

	def test_many_to_many_relations_with_nodes(self):
		"""
		It tests the many to many relations with Nodes
		"""

		node_1 = Node()
		node_1.name = "node1"
		node_1.information_retrieved = False
		node_2 = Node()
		node_2.name = "node2"
		node_2.information_retrieved = False
		db.session.add(node_1)
		db.session.add(node_2)

		execution_1 = Execution()
		execution_1.status = "x1"
		execution_2 = Execution()
		execution_2.status = "x2"
		db.session.add(execution_1)
		db.session.add(execution_2)

		db.session.commit()

		execution_1.nodes = [ node_1, node_2 ]
		execution_2.nodes = [ node_2, node_1 ]

		db.session.commit()

		execution = db.session.query(Execution).filter_by(status="x1").first()
		self.assertEquals(node_1, execution.nodes[0])
		self.assertEquals(node_2, execution.nodes[1])

		execution = db.session.query(Execution).filter_by(status="x2").first()
		self.assertEquals(node_2, execution.nodes[0])
		self.assertEquals(node_1, execution.nodes[1])

	def test_child_parent_relationship(self):
		"""
		It tests the child parent relationship between several executions
		"""

		parent = Execution()
		parent.status = "x1"
		db.session.add(parent)
		db.session.commit()

		# Empty list of children
		parent = db.session.query(Execution).filter_by(status="x1").first()
		self.assertEquals(0, len(parent.children))

		# We add childer
		child_1 = Execution()
		child_1.status = "x2"
		parent.children.append(child_1)

		child_2 = Execution()
		child_2.status = "x3"
		parent.children.append(child_2)

		db.session.commit()

		parent = db.session.query(Execution).filter_by(status="x1").first()
		self.assertEquals(2, len(parent.children))
		self.assertEquals(child_1, parent.children[0])
		self.assertEquals(child_2, parent.children[1])

		child_1 = db.session.query(Execution).filter_by(status="x2").first()
		self.assertEquals(parent, child_1.parent)

		child_2 = db.session.query(Execution).filter_by(status="x3").first()
		self.assertEquals(parent, child_2.parent)

	def test_get_number_extra_jobs(self):
		"""
		It returns the total number of extra jobs ids
		"""

		parent = Execution()
		parent.status = "x1"
		db.session.add(parent)
		db.session.commit()

		# Empty list of children
		self.assertEquals(0, parent.get_number_extra_jobs())

		# We add childer
		child_1 = Execution()
		child_1.status = "x2"
		parent.children.append(child_1)

		child_2 = Execution()
		child_2.status = Execution.__status_running__
		parent.children.append(child_2)

		db.session.commit()

		self.assertEquals(1, parent.get_number_extra_jobs())