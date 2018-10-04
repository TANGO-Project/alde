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
from models import db, GPU

class GPUMappingTest(MappingTest):
    """
    Test taht validates the correct mapping of the class GPU to be stored
    into SQL relation db
    """

    def test_crud_gpu(self):
        """ It tests the basic CRUD operations of an GPU class """

        # We erify the object is not in the db after creating it
        gpu = GPU("NVIDIA", "GF110GL")
        self.assertIsNone(gpu.id)

        # We store the object in the db
        db.session.add(gpu)

        # We recover the GPU from the db
        gpu = db.session.query(GPU).filter_by(vendor_id='NVIDIA').first()
        self.assertIsNotNone(gpu.id)
        self.assertEquals("NVIDIA", gpu.vendor_id)
        self.assertEquals("GF110GL", gpu.model_name)

        # We update the gpu
        gpu.vendor_id = "AMD"
        db.session.commit()
        gpu = db.session.query(GPU).filter_by(vendor_id='AMD').first()
        self.assertEquals("AMD", gpu.vendor_id)

        # We check the deletion
        db.session.delete(gpu)
        count = db.session.query(GPU).filter_by(vendor_id='AMD').count()
        self.assertEquals(0, count)
