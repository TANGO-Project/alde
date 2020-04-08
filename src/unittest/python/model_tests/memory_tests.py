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
from models import Memory

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
