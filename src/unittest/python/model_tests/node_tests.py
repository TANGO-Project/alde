# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from model.models import CPU, GPU, MCP, Memory, Node

class NodeTest(unittest.TestCase):
    """
    Checks the correct work of the different methods in the Node class that
    represents a Node for the Application Lifecycle Deployment Engine
    """

    def setUp(self):
        """ Initializes the node object to use in the rest of tests """

        self.node = Node("node1", True)

    def test_initialization(self):
        """ Test that an object of node class is initializated correctly """

        self.assertEquals("node1", self.node.name)
        self.assertTrue(self.node.information_retrieved)
        self.assertEquals([], self.node.architecture)
        self.assertEquals({}, self.node.status)

    def test_add_architecture_element(self):
        """
        Test that an element is correctly added to the list of
        architecture elements of a node
        """

        # We add memory to start the test
        memory = self.add_memory()
        self.assertEquals(memory, self.node.architecture[0])

        # We verify that we can not add the wrong type of element
        self.node.add_architecture_element("aasas")
        self.assertEquals(1, len(self.node.architecture))
        self.assertEquals(memory, self.node.architecture[0])

        # We verify that we can add CPU element
        cpu = CPU("Intel", "Xeon", "x86_64", "e6333", "2600Mhz", "yes", 2, "cache", "111")
        self.node.add_architecture_element(cpu)
        self.assertEquals(2, len(self.node.architecture))
        self.assertEquals(cpu, self.node.architecture[1])

        # We verify that we can add a GPU element
        gpu = GPU("NVIDIA", "Maxwell")
        self.node.add_architecture_element(gpu)
        self.assertEquals(3, len(self.node.architecture))
        self.assertEquals(gpu, self.node.architecture[2])

        # We verify that we can add a MCP element
        mcp = MCP("Intel", "Phi")
        self.node.add_architecture_element(mcp)
        self.assertEquals(4, len(self.node.architecture))
        self.assertEquals(mcp, self.node.architecture[3])

    def add_memory(self):
        """ Just adds a memory object for add memory and remove memory tests"""

        # We add one element to the node
        memory = Memory(12121, "kilobytes")
        self.node.add_architecture_element(memory)
        return memory

    def test_remove_architecture_element(self):
        """
        Unit tests that verifies that an element is correctly removed
        from the list or architecture elements of a node
        """

        # We add memory to start the test
        memory = self.add_memory()

        # We verify that we can remove it
        self.node.remove_architecture_element(memory)
        self.assertEquals(0, len(self.node.architecture))

        # We verify that removing non existem element gives no error
        self.node.remove_architecture_element("aasdfd")
        self.assertEquals(0, len(self.node.architecture))

    def test_add_status_element(self):
        """It verifies the correct work that add an element to the status"""

        # We add a slurm dictorionary to status
        key = 'slurm'
        value = {'a1': 'aaa'}
        self.node.add_status_element(key, value)
        self.assertEquals(1, len(self.node.status.keys()))
        self.assertEquals(value, self.node.status[key])

        # We verify that we can only use strings as keys
        key2 = Memory(12121, "kilobytes")
        self.node.add_status_element(key2, value)
        self.assertEquals(1, len(self.node.status.keys()))

        # We verify that we can only add dicts as values
        key3 = 'slurm2'
        value3 = Memory(12121, "kilobytes")
        self.node.add_status_element(key3, value3)
        self.assertEquals(1, len(self.node.status.keys()))
        self.assertEquals(value, self.node.status[key])

    def test_remove_status_element(self):
        """ Verifies that removing an status element works as expected """

        # We add a slurm dictorionary to status
        key = 'slurm'
        value = {'a1': 'aaa'}
        self.node.add_status_element(key, value)

        # We verify that we are able to delete it
        self.node.remove_status_element(key)
        self.assertEquals(0, len(self.node.status.keys()))

        # We verify that if the key is not there we don't get an error
        self.node.remove_status_element(key)
        self.assertEquals(0, len(self.node.status.keys()))
