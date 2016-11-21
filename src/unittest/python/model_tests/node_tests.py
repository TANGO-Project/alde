# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from model.node import Node
from model.memory import Memory

class NodeTest(unittest.TestCase):
    """Checks the correct work of the different methods in the Node class that
       represents a Node for the Application Lifecycle Deployment Engine"""

    def test_add_architecture_element(self):
        """Test that an element is correctly added to the list of
           architecture elements of a node"""

        # We define first a Node and verify that it has an empty array
        # of architecture elements
        node = Node(1, "node1", True)
        self.assertEquals(0, len(node.architecture))

        # We verify that it is possible to add a memory element to the array
        memory = Memory(12121, "kilobytes")
        node.add_architecture_element(memory)
        self.assertEquals(1, len(node.architecture))
        self.assertEquals(memory, node.architecture[0])

        # We verify that we can not add the wrong type of element
        node.add_architecture_element("aasas")
        self.assertEquals(1, len(node.architecture))
        self.assertEquals(memory, node.architecture[0])
