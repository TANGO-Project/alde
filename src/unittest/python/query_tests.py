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
from models import db, Testbed
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
