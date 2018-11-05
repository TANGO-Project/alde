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
# Unit tests that checks ALDE SQL Alchemy integration
#

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Memory

class MemoryMappingTests(MappingTest):
     """
     Test that validates the correct mapping of the class Memory to be
     stored into SQL relational db
     """

     def test_crud_memory(self):
         """ It tests the basic CRUD operations of a Memory class """

         # We verify the object is not in the db after creating it
         memory = Memory(11111, "bytes", "0x111", "writable")
         self.assertIsNone(memory.id)

         # We store the object in the db
         db.session.add(memory)

         # We recover the Memory from the db
         memory = db.session.query(Memory).filter_by(units='bytes').first()
         self.assertIsNotNone(memory.id)
         self.assertEquals(11111, memory.size)
         self.assertEquals("bytes", memory.units)
         self.assertEquals("0x111", memory.address)
         self.assertEquals("writable", memory.memory_type)

         # We update the memory
         memory.size = 0
         db.session.commit()
         memory = db.session.query(Memory).filter_by(units='bytes').first()
         self.assertEquals(0, memory.size)

         # We check the deletion
         db.session.delete(memory)
         count = db.session.query(Memory).filter_by(units='bytes').count()
         self.assertEquals(0, count)
