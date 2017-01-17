# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information


import unittest
import unittest.mock as mock
import slurm
from model.models import Testbed
from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from model.models import Testbed, Node
from model.base import db

class SlurmTests(MappingTest):
    """
    Unittests of the functions used to interact with and slurm
    testbed
    """

    command_output=b'PARTITION   AVAIL  TIMELIMIT  NODES  STATE NODELIST\nbullx          up   infinite      1  drain nd15\nbullx          up   infinite      9   idle nd[10-14,16-19]\npartners*      up    8:00:00      1  drain nd15\npartners*      up    8:00:00      9   idle nd[10-14,16-19]\ngpus           up   infinite      2 drain* nd[20-21]\ngpus           up   infinite      1   idle nd22\ngpu2075        up   infinite      1 maint* nd23\nB510_2.2GHz    up   infinite      2 maint* nd[36-37]\nB510_2.2GHz    up   infinite      2   idle nd[38-39]\nB510_2.6GHz    up   infinite      2 maint* nd[32-33]\nB510_2.6GHz    up   infinite      1  maint nd31\nB510_2.6GHz    up   infinite      8   idle nd[24-26,29-30,40-41,43]\nB510_2.6GHz    up   infinite      3   down nd[27-28,42]\nbullion        up   infinite      1  alloc nd76\nbullion_S      up   infinite      1  alloc nd80\n'

    example1 = {
                'partition_state': 'drain',
                'partition': 'bullx',
                'node_name': 'nd15',
                'partition_timelimit': 'infinite',
                'partition_avail': 'up'
               }
    example2 = {
                'partition_state': 'idle',
                'partition': 'bullx',
                'node_name': 'nd10',
                'partition_timelimit': 'infinite',
                'partition_avail': 'up'
               }
    example3 = {
                'partition_state': 'idle',
                'partition': 'B510_2.6GHz',
                'node_name': 'nd43',
                'partition_timelimit': 'infinite',
                'partition_avail': 'up'
               }
    example4 = {
                'partition_avail': 'up',
                'partition': 'B510_2.6GHz',
                'node_name': 'nd41',
                'partition_timelimit': 'infinite',
                'partition_state': 'idle'
               }

    def test_parse_sinfo_partitions(self):
        """
        Check it is possible to parse the output of the slurm
        sinfo -a
        command
        """
        output = slurm.parse_sinfo_partitions(self.command_output)

        # We verify the output
        self.assertEquals(44,len(output))
        self.assertTrue(self.example1 in output)
        self.assertTrue(self.example2 in output)
        self.assertTrue(self.example3 in output)
        self.assertTrue(self.example4 in output)

    @mock.patch('slurm.shell.execute_command')
    def test_get_nodes_testbed(self, mock_shell):
        """
        It verifies the correct work of the function get_nodes_testbed
        """
        command="sinfo"
        params=["-a"]

        # It checks first if it is type SLURM
        testbed = Testbed('x', 'false', 'xxx', 'protocol', 'xxx')

        nodes = slurm.get_nodes_testbed(testbed)
        self.assertEquals(0, len(nodes))

        # We create a testbed with local access
        testbed = Testbed('x', 'false', Testbed.slurm_category, Testbed.protocol_local, 'xxx')
        mock_shell.return_value = self.command_output
        nodes = slurm.get_nodes_testbed(testbed)

        self.assertEquals(44,len(nodes))
        self.assertTrue(self.example1 in nodes)
        self.assertTrue(self.example2 in nodes)
        self.assertTrue(self.example3 in nodes)
        self.assertTrue(self.example4 in nodes)
        mock_shell.assert_called_with(command=command, params=params)

        # We create a testbe with ssh access
        testbed = Testbed('x', 'false', Testbed.slurm_category, Testbed.protocol_ssh , "user@ssh.com")
        mock_shell.return_value = self.command_output
        nodes = slurm.get_nodes_testbed(testbed)

        self.assertEquals(44,len(nodes))
        self.assertTrue(self.example1 in nodes)
        self.assertTrue(self.example2 in nodes)
        self.assertTrue(self.example3 in nodes)
        self.assertTrue(self.example4 in nodes)
        mock_shell.assert_called_with(command=command, server="user@ssh.com", params=params)

        # Testbed with unknown protocol should return empty String
        # We create a testbe with ssh access
        testbed = Testbed('x', True, Testbed.slurm_category, "xxx" , "user@ssh.com")
        mock_shell.return_value = self.command_output
        nodes = slurm.get_nodes_testbed(testbed)

        self.assertEquals(0,len(nodes))


    @mock.patch('slurm.get_nodes_testbed')
    def test_check_nodes_in_db_for_on_line_testbeds(self, mock_get_nodes):
        """
        Test the correct work of this function
        """

        # We add two testbeds to the db
        testbed = Testbed("name1",
                            True,
                            Testbed.slurm_category,
                            "ssh",
                            "user@server",
                            ['slurm'])

        # We add some nodes to Testbed_1
        node_1 = Node("node_1", True)
        testbed.nodes = [ node_1, Node("node_2", True) ]
        node_1.disabled = True

        db.session.add(testbed)
        db.session.commit()

        #We create the expectation to retrieve a list of nodes from slurm.
        node_3 = { 'node_name': 'node_3' }
        node_1_slurm = { 'node_name': 'node_1'}
        mock_get_nodes.return_value = [ node_1_slurm, node_3 ]

        # We exectue the command
        slurm.check_nodes_in_db_for_on_line_testbeds()

        # We check we get the desired result
        node = db.session.query(Node).filter_by(name='node_3').all()
        self.assertEquals(1, len(node))
        node = node[0]
        self.assertEquals('node_3', node.name)
        self.assertTrue(node.information_retrieved)
        self.assertEquals(3, len(testbed.nodes))

        node = db.session.query(Node).filter_by(name='node_1').all()
        self.assertEquals(1, len(node))
        node = node[0]
        self.assertFalse(node.disabled)

        node = db.session.query(Node).filter_by(name='node_2').all()
        self.assertEquals(1, len(node))
        node = node[0]
        self.assertTrue(node.disabled)
