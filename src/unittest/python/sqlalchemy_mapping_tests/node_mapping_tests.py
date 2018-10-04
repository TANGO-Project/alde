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
from models import db, Node, CPU, GPU, Memory

class NodeMappingTest(MappingTest):
    """
    Test that validates teh correct mapping of the class Node to be stored
    into SQL relational db
    """

    def test_crud_node(self):
        """ It tests the basic CRUD operations of an Node class """

        # We verify the object is not in the db after creating it
        node = Node()
        node.name = "node1"
        node.information_retrieved = True
        self.assertIsNone(node.id)

        # We store the object in the db
        db.session.add(node)

        # We recover the node from the db
        node = db.session.query(Node).filter_by(name='node1').first()
        self.assertIsNotNone(node.id)
        self.assertEquals("node1", node.name)
        self.assertTrue(node.information_retrieved)

        # We update the node
        node.information_retrieved = False
        db.session.commit()
        node = db.session.query(Node).filter_by(name='node1').first()
        self.assertFalse(node.information_retrieved)

        # We check the deletion
        db.session.delete(node)
        count = db.session.query(Node).filter_by(name='node1').count()
        self.assertEquals(0, count)

    def test_node_cpu_relation(self):
        """
        Unit test that verifies that the correct relation between
        the testbed class and the node class is built
        """

        # We create a node
        node = Node()
        node.name = "node1"
        node.information_retrieved = True

        # We add several CPUs to it
        node.cpus = [
            CPU("Intel", "Xeon", "x86_64", "e6333", "2600Mhz", True, 2, "cache", "111"),
            CPU("AMD", "Zen", "x86_64", "xxxxx", "2600Mhz", True, 2, "cache", "111")
        ]

        # We save everything to the db
        db.session.add(node)
        db.session.commit()

        # We retrived and verify that the cpus are there
        node = db.session.query(Node).filter_by(name='node1').first()

        self.assertEquals(2, len(node.cpus))
        self.assertEquals("Intel", node.cpus[0].vendor_id)
        self.assertEquals("AMD", node.cpus[1].vendor_id)

        # Lets delete a cpu directly from the session
        db.session.delete(node.cpus[1])
        db.session.commit()
        node = db.session.query(Node).filter_by(name='node1').first()
        self.assertEquals(1, len(node.cpus))
        self.assertEquals("Intel", node.cpus[0].vendor_id)

    def test_node_gpu_relation(self):
        """
        Unit test that verifies that the correct relation between
        the GPU class and the node class is built
        """

        # We create a node
        node = Node()
        node.name = "node1"
        node.information_retrieved = True

        # We add several CPUs to it
        node.gpus = [
            GPU("Nvidia", "GeForce"),
            GPU("AMD", "Raedon")
        ]

        # We save everything to the db
        db.session.add(node)
        db.session.commit()

        # We retrived and verify that the gpus are there
        node = db.session.query(Node).filter_by(name='node1').first()

        self.assertEquals(2, len(node.gpus))
        self.assertEquals("Nvidia", node.gpus[0].vendor_id)
        self.assertEquals("AMD", node.gpus[1].vendor_id)

        # Lets delete a gpu directly from the session
        db.session.delete(node.gpus[1])
        db.session.commit()
        node = db.session.query(Node).filter_by(name='node1').first()
        self.assertEquals(1, len(node.gpus))
        self.assertEquals("Nvidia", node.gpus[0].vendor_id)

    def test_node_memory_relation(self):
        """
        Unit test that verifies that the correct relation between
        the Memory class and the node class is built
        """

        # We create a node
        node = Node()
        node.name = "node1"
        node.information_retrieved = True

        # We add several CPUs to it
        node.memories = [
            Memory(11111, "bytes"),
            Memory(11211, "bytes")
        ]

        # We save everything to the db
        db.session.add(node)
        db.session.commit()

        # We retrived and verify that the gpus are there
        node = db.session.query(Node).filter_by(name='node1').first()

        self.assertEquals(2, len(node.memories))
        self.assertEquals(11111, node.memories[0].size)
        self.assertEquals(11211, node.memories[1].size)

        # Lets delete a gpu directly from the session
        db.session.delete(node.memories[1])
        db.session.commit()
        node = db.session.query(Node).filter_by(name='node1').first()
        self.assertEquals(1, len(node.memories))
        self.assertEquals(11111, node.memories[0].size)
