# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
from model.memory import Memory
from model.processor import GPU

class ProcessorTest(unittest.TestCase):
    """ Check the correct work of the Processor model class and Initializes
        subclasses, that can represent things like GPU, FPGAs, CPUs, etc..."""


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
