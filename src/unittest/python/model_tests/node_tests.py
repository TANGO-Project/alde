#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.gnu.org/licenses/agpl-3.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Unit tests that checks ALDE Datamodel
#

import unittest
from models import CPU, GPU, MCP, Memory, Node

class NodeTest(unittest.TestCase):
    """
    Checks the correct work of the different methods in the Node class that
    represents a Node for the Application Lifecycle Deployment Engine
    """

    def setUp(self):
        """ Initializes the node object to use in the rest of tests """

        self.node = Node()
        self.node.name = "node1"
        self.node.information_retrieved = True

    def test_add_memory(self):
        """
        Test that memory can be added correctly to the list
        of memory elements of a node
        """

        # We verify that we can add memory
        memory = self.add_memory()
        self.assertEquals(1, len(self.node.memories))
        self.assertEquals(memory, self.node.memories[0])

        # We verify that we can not add strange elements to memory
        self.node.add_memory("asdf")
        self.assertEquals(1, len(self.node.memories))
        self.assertEquals(memory, self.node.memories[0])

    def add_memory(self):
        """ Just adds a memory object for add memory and remove memory tests"""

        # We add one element to the node
        memory = Memory(12121, "kilobytes")
        self.node.add_memory(memory)
        return memory

    def test_remove_memory(self):
        """
        Unit tests that verifies that an memory element is correctly removed
        from the list or memories elements of a node
        """

        # We add memory to start the test
        memory = self.add_memory()

        # We verify that we can remove it
        self.node.remove_memory(memory)
        self.assertEquals(0, len(self.node.memories))

        # We verify that removing non existem element gives no error
        self.node.remove_memory("aasdfd")
        self.assertEquals(0, len(self.node.memories))

    def test_add_cpu(self):
        """
        Test that cpu can be added correctly to the list
        of cpu elements of a node
        """

        # We verify that we can add memory
        cpu = self.add_cpu()
        self.assertEquals(1, len(self.node.cpus))
        self.assertEquals(cpu, self.node.cpus[0])

        # We verify that we can not add strange elements to memory
        self.node.add_cpu("asdf")
        self.assertEquals(1, len(self.node.cpus))
        self.assertEquals(cpu, self.node.cpus[0])

    def add_cpu(self):
        """ Just adds a memory object for add memory and remove memory tests"""

        # We add one element to the node
        cpu = CPU("Intel", "Xeon", "x86_64", "e6333", "2600Mhz", "yes", 2, "cache", "111")
        self.node.add_cpu(cpu)
        return cpu

    def test_remove_cpu(self):
        """
        Unit tests that verifies that an cpu element is correctly removed
        from the list or cpus elements of a node
        """

        # We add memory to start the test
        cpu = self.add_cpu()

        # We verify that we can remove it
        self.node.remove_cpu(cpu)
        self.assertEquals(0, len(self.node.cpus))

        # We verify that removing non existem element gives no error
        self.node.remove_cpu("aasdfd")
        self.assertEquals(0, len(self.node.cpus))

    def test_add_gpu(self):
        """
        Test that gpu can be added correctly to the list
        of gpu elements of a node
        """

        # We verify that we can add memory
        gpu = self.add_gpu()
        self.assertEquals(1, len(self.node.gpus))
        self.assertEquals(gpu, self.node.gpus[0])

        # We verify that we can not add strange elements to memory
        self.node.add_gpu("asdf")
        self.assertEquals(1, len(self.node.gpus))
        self.assertEquals(gpu, self.node.gpus[0])

    def add_gpu(self):
        """ Just adds a gpu object for add gpu and remove gpu tests"""

        # We add one element to the node
        gpu = GPU("NVIDIA", "Maxwell")
        self.node.add_gpu(gpu)
        return gpu

    def test_remove_gpu(self):
        """
        Unit tests that verifies that an gpu element is correctly removed
        from the list or gpus elements of a node
        """

        # We add gpue to start the test
        gpu = self.add_gpu()

        # We verify that we can remove it
        self.node.remove_gpu(gpu)
        self.assertEquals(0, len(self.node.gpus))

        # We verify that removing non existem element gives no error
        self.node.remove_gpu("aasdfd")
        self.assertEquals(0, len(self.node.gpus))

    def test_add_mcp(self):
        """
        Test that mcp can be added correctly to the list
        of mcp elements of a node
        """

        # We verify that we can add memory
        mcp = self.add_mcp()
        self.assertEquals(1, len(self.node.mcps))
        self.assertEquals(mcp, self.node.mcps[0])

        # We verify that we can not add strange elements to memory
        self.node.add_mcp("asdf")
        self.assertEquals(1, len(self.node.mcps))
        self.assertEquals(mcp, self.node.mcps[0])

    def add_mcp(self):
        """ Just adds a mcp object for add mcp and remove mcp tests"""

        # We add one element to the node
        mcp = MCP("Intel", "Phi")
        self.node.add_mcp(mcp)
        return mcp

    def test_remove_cpu(self):
        """
        Unit tests that verifies that an mcp element is correctly removed
        from the list or cpus elements of a node
        """

        # We add memory to start the test
        mcp = self.add_mcp()

        # We verify that we can remove it
        self.node.remove_mcp(mcp)
        self.assertEquals(0, len(self.node.mcps))

        # We verify that removing non existem element gives no error
        self.node.remove_mcp("aasdfd")
        self.assertEquals(0, len(self.node.mcps))

    def test_add_status(self):
        """It verifies the correct work that add an element to the status"""

        # We add a slurm dictorionary to status
        key = 'slurm'
        value = {'a1': 'aaa'}
        self.node.add_status(key, value)
        self.assertEquals(1, len(self.node.status.keys()))
        self.assertEquals(value, self.node.status[key])

        # We verify that we can only use strings as keys
        key2 = Memory(12121, "kilobytes")
        self.node.add_status(key2, value)
        self.assertEquals(1, len(self.node.status.keys()))

        # We verify that we can only add dicts as values
        key3 = 'slurm2'
        value3 = Memory(12121, "kilobytes")
        self.node.add_status(key3, value3)
        self.assertEquals(1, len(self.node.status.keys()))
        self.assertEquals(value, self.node.status[key])

    def test_remove_status(self):
        """ Verifies that removing an status element works as expected """

        # We add a slurm dictorionary to status
        key = 'slurm'
        value = {'a1': 'aaa'}
        self.node.add_status(key, value)

        # We verify that we are able to delete it
        self.node.remove_status(key)
        self.assertEquals(0, len(self.node.status.keys()))

        # We verify that if the key is not there we don't get an error
        self.node.remove_status(key)
        self.assertEquals(0, len(self.node.status.keys()))
