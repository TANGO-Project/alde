# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from model.testbed import Testbed

class TestbedMappingTest(MappingTest):
    """
    Test of series to validate the correct mapping of the class
    Testbed to be stored into an SQL relational db
    """

    def test_crud_testbed(self):
        """ It tests the basic CRUD operations of an Testbed class """

        # We verify the object is not in the db after creating it
        testbed = Testbed("name", True, "slurm", "ssh", "user@server", ['slurm'])
        self.assertIsNone(testbed.id)

        # We store the boject in the db
        self.session.add(testbed)

        # We recover the testbed from the db
        testbed = self.session.query(Testbed).filter_by(name='name').first()
        self.assertIsNotNone(testbed.id)
        self.assertEquals('name', testbed.name)
        self.assertTrue(testbed.on_line)
        self.assertEquals('ssh', testbed.protocol)
        self.assertEquals("user@server", testbed.endpoint)

        # We update the testbed
        testbed.on_line = False
        self.session.commit()
        testbed = self.session.query(Testbed).filter_by(name='name').first()
        self.assertFalse(testbed.on_line)

        # We check the deletion
        self.session.delete(testbed)
        count = self.session.query(Testbed).filter_by(name='name').count()
        self.assertEquals(0, count)
