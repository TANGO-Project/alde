# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

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
