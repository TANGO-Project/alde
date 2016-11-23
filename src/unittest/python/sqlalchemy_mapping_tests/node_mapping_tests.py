# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from model.node import Node

class NodeMappingTest(MappingTest):
    """
    Test that validates teh correct mapping of the class Node to be stored
    into SQL relational db
    """

    def test_crud_node(self):
        """ It tests the basic CRUD operations of an Node class """

        # We verify the object is not in the db after creating it
        node = Node("node1", True)
        self.assertIsNone(node.id)

        # We store the object in the db
        self.session.add(node)

        # We recover the node from the db
        node = self.session.query(Node).filter_by(name='node1').first()
        self.assertIsNotNone(node.id)
        self.assertEquals("node1", node.name)
        self.assertTrue(node.information_retrieved)

        # We update the node
        node.information_retrieved = False
        self.session.commit()
        node = self.session.query(Node).filter_by(name='node1').first()
        self.assertFalse(node.information_retrieved)

        # We check the deletion
        self.session.delete(node)
        count = self.session.query(Node).filter_by(name='node1').count()
        self.assertEquals(0, count)
