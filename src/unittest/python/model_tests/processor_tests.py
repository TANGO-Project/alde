# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from model.models import Processor, GPU, CPU, MCP, Memory

class ProcessorTest(unittest.TestCase):
    """ Check the correct work of the Processor model class and Initializes
        subclasses, that can represent things like GPU, FPGAs, CPUs, etc..."""

    def test_init_methods(self):
        """Checks that the variables are correctly set"""

        # Processor class
        processor = Processor("x1", "x2")
        self.assertEquals("x1", processor.vendor_id)
        self.assertEquals("x2", processor.model_name)

        # CPU class
        cpu = CPU("Intel", "Xeon", "x86_64", "e6333", "2600Mhz", "yes", 2, "cache", "111")
        self.assertEquals("Intel", cpu.vendor_id)
        self.assertEquals("Xeon", cpu.model_name)
        self.assertEquals("x86_64", cpu.arch)
        self.assertEquals("2600Mhz", cpu.cpu_speed)
        self.assertEquals("yes", cpu.fpu)
        self.assertEquals(2, cpu.cpu_cores)
        self.assertEquals("cache", cpu.cache)
        self.assertEquals("111", cpu.flags)

        # GPU
        gpu = GPU("AMD", "Raedon")
        self.assertEquals("AMD", gpu.vendor_id)
        self.assertEquals("Raedon", gpu.model_name)
        self.assertEquals([], gpu.memory)

        # MCP
        mcp = MCP("Intel", "Phi")
        self.assertEquals("Intel", mcp.vendor_id)
        self.assertEquals("Phi", mcp.model_name)
        self.assertEquals([], mcp.memory)

    def test_add_memory_gpu(self):
        """Test that we can correctly add memory to a GPU moemory array"""

        # We create an initial GPU
        gpu = GPU("NVIDIA", "GF110GL")
        self.assertEquals(0, len(gpu.memory))

        # We add a Memory element
        memory = Memory(1111, "kilobytes")
        gpu.add_memory(memory)
        self.assertEquals(1, len(gpu.memory))
        self.assertEquals(memory, gpu.memory[0])

        # We verify that we can not add memory of the wrong type
        gpu.add_memory("xxx")
        self.assertEquals(1, len(gpu.memory))
        self.assertEquals(memory, gpu.memory[0])

    def test_remove_memory(self):
        """We verify it is possible to delete a memory element"""

        # We create an initial GPU
        gpu = GPU("NVIDIA", "GF110GL")
        print(len(gpu.memory))
        self.assertEquals(0, len(gpu.memory))

        # We add a Memory element
        memory = Memory(1111, "kilobytes")
        gpu.add_memory(memory)
        self.assertEquals(1, len(gpu.memory))

        # We remove it
        gpu.remove_memory(memory)
        self.assertEquals(0, len(gpu.memory))

        # We verify that removing an inexistent elements gives no error
        gpu.remove_memory("xxx")
        self.assertEquals(0, len(gpu.memory))
