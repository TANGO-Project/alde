# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information



from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from model.models import db, Testbed
import query

class QueryTests(MappingTest):
    """
    Test a set of helpers querys to perform CRUD operations against the db
    """

    def test_get_slurm_on_line_testbeds(self):
        """
        It sees if it is possible to get from the db only the on-line
        testbeds that are from type slurm
        """

        # We add shome testbeds to the temporal db
        testbed_1 = Testbed("name1",
                            True,
                            Testbed.slurm_category,
                            "ssh",
                            "user@server",
                            ['slurm'])
        testbed_2 = Testbed("name2",
                            False,
                            Testbed.slurm_category,
                            "ssh",
                            "user@server",
                            ['slurm'])
        testbed_3 = Testbed("name3",
                            True,
                            "xxx",
                            "ssh",
                            "user@server",
                            ['slurm'])
        testbed_4 = Testbed("name4",
                            True,
                            Testbed.slurm_category,
                            "ssh",
                            "user@server",
                            ['slurm'])

        # We store the object in the db
        db.session.add(testbed_1)
        db.session.add(testbed_2)
        db.session.add(testbed_3)
        db.session.add(testbed_4)

        testbeds = query.get_slurm_online_testbeds()
        self.assertEquals(2, len(testbeds))
        self.assertEquals("name1", testbeds[0].name)
        self.assertEquals("name4", testbeds[1].name)
