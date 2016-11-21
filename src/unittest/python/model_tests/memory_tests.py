# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information


import unittest
from model.memory import Memory

class MemoryTests(unittest.TestCase):
    """Verifies the correct work of the class Memory"""

    def test_initialization(self):
        """Verifies that the initialization of the values of a Memory object"""

        # Adding default values
        memory_1 = Memory(111, "kilobytes", "0x111", "writetable")
        self.assertEquals(111, memory_1.size)
        self.assertEquals("kilobytes", memory_1.units)
        self.assertEquals("0x111", memory_1.address)
        self.assertEquals("writetable", memory_1.memory_type)

        ## Without default values
        memory_2 = Memory(2, "megabytes")
        self.assertEquals(2, memory_2.size)
        self.assertEquals("megabytes", memory_2.units)
        self.assertEquals("", memory_2.address)
        self.assertEquals("", memory_2.memory_type)
