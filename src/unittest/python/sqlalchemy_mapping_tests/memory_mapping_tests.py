# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from model.models import Memory
from model.base import db

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
