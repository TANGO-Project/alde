# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from model.models import Testbed, Node
from model.base import db

class TestbedMappingTest(MappingTest):
    """
    Test of series to validate the correct mapping of the class
    Testbed to be stored into an SQL relational db
    """

    def test_crud_testbed(self):
        """ It tests the basic CRUD operations of an Testbed class """

        # We verify the object is not in the db after creating it
        testbed = Testbed("name", True, "slurm", "ssh", "user@server", ['slurm'])
        self.assertIsNone(testbed.id)

        # We store the object in the db
        db.session.add(testbed)

        # We recover the testbed from the db
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertIsNotNone(testbed.id)
        self.assertEquals('name', testbed.name)
        self.assertTrue(testbed.on_line)
        self.assertEquals('ssh', testbed.protocol)
        self.assertEquals("user@server", testbed.endpoint)

        # We update the testbed
        testbed.on_line = False
        db.session.commit()
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertFalse(testbed.on_line)

        # We check the deletion
        db.session.delete(testbed)
        count = db.session.query(Testbed).filter_by(name='name').count()
        self.assertEquals(0, count)

    def test_testbed_node_relation(self):
        """
        Unit test that verifies that the correct relation between
        the testbed class and the node class is built
        """

        # We create a testbed
        testbed = Testbed("name", True, "slurm", "ssh", "user@server", ['slurm'])

        # We create several nodes
        testbed.nodes = [
                           Node("node1", True),
                           Node("node2", False),
                           Node("node3", True) ]

        # We save everything to the db
        db.session.add(testbed)
        db.session.commit()

        # We retrieve and verify that the nodes are there
        testbed = db.session.query(Testbed).filter_by(name='name').first()

        self.assertEquals(3, len(testbed.nodes))
        self.assertEquals("node1", testbed.nodes[0].name)
        self.assertTrue(testbed.nodes[0].information_retrieved)
        self.assertEquals("node2", testbed.nodes[1].name)
        self.assertFalse(testbed.nodes[1].information_retrieved)
        self.assertEquals("node3", testbed.nodes[2].name)
        self.assertTrue(testbed.nodes[2].information_retrieved)

        # lets remove a node from testbed
        testbed.remove_node(testbed.nodes[2])

        # We commit the state and it should be updated
        db.session.commit()
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertEquals(2, len(testbed.nodes))
        self.assertEquals("node1", testbed.nodes[0].name)
        self.assertTrue(testbed.nodes[0].information_retrieved)
        self.assertEquals("node2", testbed.nodes[1].name)
        self.assertFalse(testbed.nodes[1].information_retrieved)

        # Lets delete the node directly from the session
        db.session.delete(testbed.nodes[1])
        db.session.commit()
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertEquals(1, len(testbed.nodes))
        self.assertEquals("node1", testbed.nodes[0].name)
        self.assertTrue(testbed.nodes[0].information_retrieved)

        # It should be only one node in the db
        nodes = db.session.query(Node).all()
        self.assertEquals(2, len(nodes))
        self.assertEquals("node1", nodes[0].name)
        self.assertTrue(nodes[0].information_retrieved)
        self.assertIsNotNone(nodes[0].testbed)
        self.assertEquals("node3", nodes[1].name)
        self.assertTrue(nodes[1].information_retrieved)
        self.assertIsNone(nodes[1].testbed)
