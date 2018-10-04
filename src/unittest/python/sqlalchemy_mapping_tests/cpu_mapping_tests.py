#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
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
from models import db, CPU

class CPUMappingTest(MappingTest):
    """
    Test taht validates the correct mapping of the class CPU to be stored
    into SQL relation db
    """

    def test_crud_cpu(self):
        """ It tests the basic CRUD operations of an CPU class """

        # We erify the object is not in the db after creating it
        cpu = CPU("Intel", "Xeon", "x86_64", "e6333", "2600Mhz", True, 2, "cache", "111")
        self.assertIsNone(cpu.id)

        # We store the object in the db
        db.session.add(cpu)

        # We recover the GPU from the db
        cpu = db.session.query(CPU).filter_by(vendor_id='Intel').first()
        self.assertIsNotNone(cpu.id)
        self.assertEquals("Intel", cpu.vendor_id)
        self.assertEquals("Xeon", cpu.model_name)
        self.assertEquals("x86_64", cpu.arch)
        self.assertEquals("e6333", cpu.model)
        self.assertEquals("2600Mhz", cpu.speed)
        self.assertTrue(cpu.fpu)
        self.assertEquals(2, cpu.cores)
        self.assertEquals("cache", cpu.cache)
        self.assertEquals("111", cpu.flags)

        # We update the gpu
        cpu.vendor_id = "AMD"
        db.session.commit()
        cpu = db.session.query(CPU).filter_by(vendor_id='AMD').first()
        self.assertEquals("AMD", cpu.vendor_id)

        # We check the deletion
        db.session.delete(cpu)
        count = db.session.query(CPU).filter_by(vendor_id='AMD').count()
        self.assertEquals(0, count)
