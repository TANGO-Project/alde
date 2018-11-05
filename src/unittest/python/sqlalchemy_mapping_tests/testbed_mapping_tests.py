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
from models import db, Testbed, Node

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

        # We store the object in the db
        db.session.add(testbed)

        # We recover the testbed from the db
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertIsNotNone(testbed.id)
        self.assertEquals('name', testbed.name)
        self.assertTrue(testbed.on_line)
        self.assertEquals('ssh', testbed.protocol)
        self.assertEquals("user@server", testbed.endpoint)

        # We update the testbed
        testbed.on_line = False
        db.session.commit()
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertFalse(testbed.on_line)

        # Checking the pickle format
        testbed.package_formats = [ 'pepito', 'fulanito']
        db.session.commit()
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertEquals('pepito', testbed.package_formats[0])
        self.assertEquals('fulanito', testbed.package_formats[1])


        # We check the deletion
        db.session.delete(testbed)
        count = db.session.query(Testbed).filter_by(name='name').count()
        self.assertEquals(0, count)

    def test_testbed_node_relation(self):
        """
        Unit test that verifies that the correct relation between
        the testbed class and the node class is built
        """

        # We create a testbed
        testbed = Testbed("name", True, "slurm", "ssh", "user@server", ['slurm'])

        # We create several nodes
        node_1 = Node()
        node_1.name = "node1"
        node_1.information_retrieved = True
        node_2 = Node()
        node_2.name = "node2"
        node_2.information_retrieved = False
        node_3 = Node()
        node_3.name = "node3"
        node_3.information_retrieved = True
        testbed.nodes = [ node_1, node_2, node_3 ]

        # We save everything to the db
        db.session.add(testbed)
        db.session.commit()

        # We retrieve and verify that the nodes are there
        testbed = db.session.query(Testbed).filter_by(name='name').first()

        self.assertEquals(3, len(testbed.nodes))
        self.assertEquals("node1", testbed.nodes[0].name)
        self.assertTrue(testbed.nodes[0].information_retrieved)
        self.assertEquals("node2", testbed.nodes[1].name)
        self.assertFalse(testbed.nodes[1].information_retrieved)
        self.assertEquals("node3", testbed.nodes[2].name)
        self.assertTrue(testbed.nodes[2].information_retrieved)

        # lets remove a node from testbed
        testbed.remove_node(testbed.nodes[2])

        # We commit the state and it should be updated
        db.session.commit()
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertEquals(2, len(testbed.nodes))
        self.assertEquals("node1", testbed.nodes[0].name)
        self.assertTrue(testbed.nodes[0].information_retrieved)
        self.assertEquals("node2", testbed.nodes[1].name)
        self.assertFalse(testbed.nodes[1].information_retrieved)

        # Lets delete the node directly from the session
        db.session.delete(testbed.nodes[1])
        db.session.commit()
        testbed = db.session.query(Testbed).filter_by(name='name').first()
        self.assertEquals(1, len(testbed.nodes))
        self.assertEquals("node1", testbed.nodes[0].name)
        self.assertTrue(testbed.nodes[0].information_retrieved)

        # It should be only one node in the db
        nodes = db.session.query(Node).all()
        self.assertEquals(2, len(nodes))
        self.assertEquals("node1", nodes[0].name)
        self.assertTrue(nodes[0].information_retrieved)
        self.assertIsNotNone(nodes[0].testbed)
        self.assertEquals("node3", nodes[1].name)
        self.assertTrue(nodes[1].information_retrieved)
        self.assertIsNone(nodes[1].testbed)


    def test_extra_config(self):
        """
        Test the storing of JSON into the entity extra_config param
        """

        testbed = Testbed("name", True, "slurm", "ssh", "user@server", ['slurm'])

        db.session.add(testbed)

        testbed.extra_config = { "enqueue_compss_sc_cfg": "nova.cfg" }

        db.session.commit()

        testbed = db.session.query(Testbed).filter_by(name='name').first()

        self.assertEquals('nova.cfg', testbed.extra_config['enqueue_compss_sc_cfg'])

        testbed.extra_config['pepe'] = 'pepito'

        db.session.commit()

        testbed = db.session.query(Testbed).filter_by(name='name').first()

        self.assertEquals('nova.cfg', testbed.extra_config['enqueue_compss_sc_cfg'])
        self.assertEquals('pepito', testbed.extra_config['pepe'])

        del testbed.extra_config['pepe']
        db.session.flush()
        db.session.commit()

        testbed = db.session.query(Testbed).filter_by(name='name').first()
        with self.assertRaises(KeyError) as raises:
            variable = testbed.extra_config['pepe']
