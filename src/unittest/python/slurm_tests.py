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
# Unit tests that checks ALDE slurm module
#


import unittest
import unittest.mock as mock
import slurm
import re
import inventory
from models import Testbed
from sqlalchemy_mapping_tests.mapping_tests import MappingTest
from models import db, Testbed, Node, CPU, Memory
from testfixtures import LogCapture

class SlurmTests(MappingTest):
    """
    Unittests of the functions used to interact with and slurm
    testbed
    """

    command_output=b'PARTITION   AVAIL  TIMELIMIT  NODES  STATE NODELIST\nbullx          up   infinite      1  drain nd15\nbullx          up   infinite      9   idle nd[10-14,16-19]\npartners*      up    8:00:00      1  drain nd15\npartners*      up    8:00:00      9   idle nd[10-14,16-19]\ngpus           up   infinite      2 drain* nd[20-21]\ngpus           up   infinite      1   idle nd22\ngpu2075        up   infinite      1 maint* nd23\nB510_2.2GHz    up   infinite      2 maint* nd[36-37]\nB510_2.2GHz    up   infinite      2   idle nd[38-39]\nB510_2.6GHz    up   infinite      2 maint* nd[32-33]\nB510_2.6GHz    up   infinite      1  maint nd31\nB510_2.6GHz    up   infinite      8   idle nd[24-26,29-30,40-41,43]\nB510_2.6GHz    up   infinite      3   down nd[27-28,42]\nbullion        up   infinite      1  alloc nd76\nbullion_S      up   infinite      1  alloc nd80\n'
    command_scontrol_output=b'NodeName=nd80 Arch=x86_64 CoresPerSocket=18 CPUAlloc=288 CPUErr=0 CPUTot=288 CPULoad=128.35 Features=(null) Gres=(null) NodeAddr=nd80 NodeHostName=nd80 Version=14.11 OS=Linux RealMemory=6850663 AllocMem=0 Sockets=16 Boards=1 State=ALLOCATED ThreadsPerCore=1 TmpDisk=0 Weight=1 BootTime=2016-11-15T14:39:36 SlurmdStartTime=2017-01-10T08:43:22 CurrentWatts=4208 LowestJoules=4522674 ConsumedJoules=7611934651 ExtSensorsJoules=n/s ExtSensorsWatts=0 ExtSensorsTemp=n/s\nNodeName=nd23 Arch=x86_64 CoresPerSocket=4 CPUAlloc=0 CPUErr=0 CPUTot=8 CPULoad=0.59 Features=(null) Gres=gpu:tesla2075:2,bandwidth:lustre:no_consume:4G NodeAddr=nd23 NodeHostName=nd23 Version=14.11 OS=Linux RealMemory=24018 AllocMem=0 Sockets=2 Boards=1 State=MAINT ThreadsPerCore=1 TmpDisk=0 Weight=1 BootTime=2016-09-14T08:38:02 SlurmdStartTime=2017-01-24T17:31:11 CurrentWatts=n/s LowestJoules=n/s ConsumedJoules=n/s ExtSensorsJoules=n/s ExtSensorsWatts=0 ExtSensorsTemp=n/s Reason=Node unexpectedly rebooted [slurm@2016-09-14T08:37:00]\nNodeName=nd22 Arch=x86_64 CoresPerSocket=4 CPUAlloc=0 CPUErr=0 CPUTot=8 CPULoad=0.67 Features=(null) Gres=gpu:tesla2050:2 NodeAddr=nd22 NodeHostName=nd22 Version=14.11 OS=Linux RealMemory=24018 AllocMem=0 Sockets=2 Boards=1 State=MAINT ThreadsPerCore=1 TmpDisk=0 Weight=1 BootTime=2016-09-14T08:38:05 SlurmdStartTime=2017-01-24T17:33:47 CurrentWatts=n/s LowestJoules=n/s ConsumedJoules=n/s ExtSensorsJoules=n/s ExtSensorsWatts=0 ExtSensorsTemp=n/s\n'

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

    def _create_initial_db_data(self):
        """
        This method creates some initial data in the db that is employed by
        some of the tests here.
        """

        # We add two testbeds to the db
        testbed = Testbed("name1",
                            True,
                            Testbed.slurm_category,
                            "ssh",
                            "user@server",
                            ['slurm'])

        # We add some nodes to Testbed_1
        node_1 = Node()
        node_1.name = "node_1"
        node_1.information_retrieved = True
        node_2 = Node()
        node_2.name = "node_2"
        node_2.information_retrieved = True
        testbed.nodes = [ node_1,  node_2]
        node_1.disabled = True

        db.session.add(testbed)
        db.session.commit()

        return testbed, node_1, node_2

    @mock.patch('slurm.get_nodes_testbed')
    def test_check_nodes_in_db_for_on_line_testbeds(self, mock_get_nodes):
        """
        Test the correct work of this function
        """
        l = LogCapture() # we cature the logger

        # We store some data in the db for the test.
        testbed, node_1, node_2 = self._create_initial_db_data()

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

        # Checking that we are logging the correct messages
        l.check(
            ('root', 'INFO', 'Checking node info for testbed: name1'),
            ('root', 'INFO', 'Adding a new node: node_3 to testbed: name1'),
            ('root', 'INFO', 'Enabling node: node_1'),
            ('root', 'INFO', 'Disabling node: node_2')
            )
        l.uninstall() # We uninstall the capture of the logger

    @mock.patch('linux_probes.cpu_info_parser.get_cpuinfo_node')
    def test_update_cpu_node_information(self, mock_parser):
        """
        Test that the correct work of this function
        """
        l = LogCapture() # we cature the logger

        # We store some data in the db for the test.
        testbed, node_1, node_2 = self._create_initial_db_data()

        node_3 =  Node()
        node_3.name = "node_3"
        node_3.information_retrieved = True
        testbed.nodes.append(node_3)

        node_3.cpus = [CPU("Intel", "Xeon", "x86_64", "e6333", "2600Mhz", True, 2, "cache", "111")]

        # So, testbed has 3 nodes, one disabled and the other ones enabled
        db.session.commit()

        cpus_result = [CPU("Intel2", "Xeon2", "x86_64", "e6333", "2600Mhz", True, 2, "cache", "111"),
                       CPU("Intel3", "Xeon3", "x86_64", "e6333", "2600Mhz", True, 2, "cache", "111")]

        mock_parser.return_value = cpus_result

        slurm.update_cpu_node_information()

        # We verify the results
        self.assertEquals(0, len(db.session.query(CPU).filter_by(vendor_id="Intel").all()))
        self.assertEquals(1, len(db.session.query(CPU).filter_by(vendor_id="Intel2").all()))
        self.assertEquals(1, len(db.session.query(CPU).filter_by(vendor_id="Intel3").all()))

        calls = [ mock.call(testbed, node_2), mock.call(testbed, node_3)]
        mock_parser.assert_has_calls(calls)
        self.assertEquals(2, mock_parser.call_count)

        # In case an error occours retrieving the information
        mock_parser.return_value = []

        slurm.update_cpu_node_information()

        calls = [ mock.call(testbed, node_2), mock.call(testbed, node_3)]
        mock_parser.assert_has_calls(calls)
        self.assertEquals(4, mock_parser.call_count)

        # Checking that we are logging the correct messages
        l.check(
            ('root', 'INFO', 'Updating CPU info for node: node_2'),
            ('root', 'INFO', 'Updating CPU info for node: node_3'),
            ('root', 'ERROR', 'Impossible to update CPU info for node: node_2'),
            ('root', 'ERROR', 'Impossible to update CPU info for node: node_3')
            )
        l.uninstall() # We uninstall the capture of the logger

    def test_parse_scontrol_information(self):
        """
        Unit test to verify the correct work of the function:
        parse_scontrol_information
        """

        nodes_info = slurm.parse_scontrol_information(self.command_scontrol_output)

        self.assertEquals(4, len(nodes_info))
        self.assertEquals("nd80", nodes_info[0]['NodeName'])
        self.assertEquals("x86_64", nodes_info[0]['Arch'])
        self.assertEquals("18", nodes_info[0]['CoresPerSocket'])
        self.assertEquals("6850663", nodes_info[0]['RealMemory'])
        self.assertEquals("1", nodes_info[0]['ThreadsPerCore'])
        self.assertEquals("16", nodes_info[0]['Sockets'])
        self.assertEquals("nd23", nodes_info[1]['NodeName'])
        self.assertEquals("gpu:tesla2075:2,bandwidth:lustre:no_consume:4G", nodes_info[1]['Gres'])
        self.assertEquals("nd22", nodes_info[2]['NodeName'])

    @mock.patch('slurm.shell.execute_command')
    def test_get_node_information(self, mock_shell):
        """
        It verifies the correct work of the function get_nodes_testbed
        """
        command = "scontrol"
        params = ["-o", "--all", "show", "node"]

        # It checks first if it is type SLURM
        testbed = Testbed('x', 'false', 'xxx', 'protocol', 'xxx')

        nodes = slurm.get_node_information(testbed)
        self.assertEquals(0, len(nodes))

        # We create a testbed with local access
        testbed = Testbed('x', 'false', Testbed.slurm_category, Testbed.protocol_local, 'xxx')
        mock_shell.return_value = self.command_scontrol_output
        nodes_info = slurm.get_node_information(testbed)

        self.assertEquals(4, len(nodes_info))
        self.assertEquals("nd80", nodes_info[0]['NodeName'])
        self.assertEquals("x86_64", nodes_info[0]['Arch'])
        self.assertEquals("18", nodes_info[0]['CoresPerSocket'])
        self.assertEquals("6850663", nodes_info[0]['RealMemory'])
        self.assertEquals("1", nodes_info[0]['ThreadsPerCore'])
        self.assertEquals("16", nodes_info[0]['Sockets'])
        self.assertEquals("nd23", nodes_info[1]['NodeName'])
        self.assertEquals("gpu:tesla2075:2,bandwidth:lustre:no_consume:4G", nodes_info[1]['Gres'])
        self.assertEquals("nd22", nodes_info[2]['NodeName'])
        mock_shell.assert_called_with(command=command, params=params)

        # We create a testbe with ssh access
        testbed = Testbed('x', 'false', Testbed.slurm_category, Testbed.protocol_ssh , "user@ssh.com")
        mock_shell.return_value = self.command_scontrol_output
        nodes_info = slurm.get_node_information(testbed)

        self.assertEquals(4, len(nodes_info))
        self.assertEquals("nd80", nodes_info[0]['NodeName'])
        self.assertEquals("x86_64", nodes_info[0]['Arch'])
        self.assertEquals("18", nodes_info[0]['CoresPerSocket'])
        self.assertEquals("6850663", nodes_info[0]['RealMemory'])
        self.assertEquals("1", nodes_info[0]['ThreadsPerCore'])
        self.assertEquals("16", nodes_info[0]['Sockets'])
        self.assertEquals("nd23", nodes_info[1]['NodeName'])
        self.assertEquals("gpu:tesla2075:2,bandwidth:lustre:no_consume:4G", nodes_info[1]['Gres'])
        self.assertEquals("nd22", nodes_info[2]['NodeName'])
        mock_shell.assert_called_with(command=command, server="user@ssh.com", params=params)

        # Testbed with unknown protocol should return empty String
        # We create a testbe with ssh access
        testbed = Testbed('x', True, Testbed.slurm_category, "xxx" , "user@ssh.com")
        nodes = slurm.get_node_information(testbed)

        self.assertEquals(0,len(nodes))

    @mock.patch('shell.execute_command')
    def test_update_node_information(self, mock_shell):
        """
        Test that the correct work of this function
        """
        l = LogCapture() # we cature the logger
        command = "scontrol"
        params = ["-o", "--all", "show", "node"]

        # We store some data in the db for the test.
        # We add two testbeds to the db
        testbed = Testbed("name1",
                            True,
                            Testbed.slurm_category,
                            Testbed.protocol_ssh,
                            "user@server",
                            ['slurm'])

        # We add some nodes to Testbed_1
        node_1 = Node()
        node_1.name = "nd80"
        node_1.information_retrieved = True
        node_2 = Node()
        node_2.name = "nd23"
        node_2.information_retrieved = True
        testbed.nodes = [ node_1,  node_2]
        node_1.disabled = True

        db.session.add(testbed)
        db.session.commit()

        # We mock the command call
        mock_shell.return_value = self.command_scontrol_output

        slurm.update_node_information()

        # We verify the results
        node_80 = db.session.query(Node).filter_by(name='nd80').first()
        node_23 = db.session.query(Node).filter_by(name='nd23').first()
        self.assertEquals('ALLOCATED', node_80.state)
        self.assertEquals(1, len(node_80.memories))
        self.assertEquals(Memory.MEGABYTE, node_80.memories[0].units)
        self.assertEquals(6850663, node_80.memories[0].size)
        self.assertEquals(0,len(node_80.gpus))

        self.assertEquals('MAINT', node_23.state)
        self.assertEquals(1, len(node_23.memories))
        self.assertEquals(Memory.MEGABYTE, node_23.memories[0].units)
        self.assertEquals(24018, node_23.memories[0].size)
        self.assertEquals(2,len(node_23.gpus))
        self.assertEquals('Nvidia', node_23.gpus[0].vendor_id)
        self.assertEquals('Nvidia TESLA C2075', node_23.gpus[0].model_name)
        self.assertEquals('Nvidia', node_23.gpus[1].vendor_id)
        self.assertEquals('Nvidia TESLA C2075', node_23.gpus[1].model_name)

        mock_shell.assert_called_with(command=command, server="user@server", params=params)
        self.assertEquals(1, mock_shell.call_count)

        # Checking that we are logging the correct messages
        l.check(
            ('root', 'INFO', 'Updating information for node: nd80 if necessary'),
            ('root', 'INFO', 'Updating memory information for node: nd80'),
            ('root', 'INFO', 'Updating information for node: nd23 if necessary'),
            ('root', 'INFO', 'Updating memory information for node: nd23'),
            ('root', 'INFO', 'Updating gpu information for node: nd23')
            )
        l.uninstall() # We uninstall the capture of the logger

    def test_parse_gre_field_info(self):
        """
        Checks this function works correctly
        """

        # We overwrite first the url of the inventory file db
        inventory.GPU_FILE = "gpu_cards_list.json"

        # Test starts here
        gre_text_example='gpu:tesla2075:2,bandwidth:lustre:no_consume:4G'
        resources = slurm.parse_gre_field_info(gre_text_example)

        self.assertEquals(2, len(resources['gpu']))
        self.assertEquals('Nvidia', resources['gpu'][0].vendor_id)
        self.assertEquals('Nvidia TESLA C2075', resources['gpu'][0].model_name)
        self.assertEquals('Nvidia', resources['gpu'][1].vendor_id)
        self.assertEquals('Nvidia TESLA C2075', resources['gpu'][1].model_name)

        gre_text_example='cpu:xxx1:1,gpu:tesla870,gpu:tesla2075:2,bandwidth:lustre:no_consume:4G'
        resources = slurm.parse_gre_field_info(gre_text_example)

        self.assertEquals(3, len(resources['gpu']))
        self.assertEquals('Nvidia', resources['gpu'][0].vendor_id)
        self.assertEquals('Nvidia TESLA C870', resources['gpu'][0].model_name)
        self.assertEquals('Nvidia', resources['gpu'][1].vendor_id)
        self.assertEquals('Nvidia TESLA C2075', resources['gpu'][1].model_name)
        self.assertEquals('Nvidia', resources['gpu'][2].vendor_id)
        self.assertEquals('Nvidia TESLA C2075', resources['gpu'][2].model_name)

        gre_text_example='gpu:teslak20:2'
        resources = slurm.parse_gre_field_info(gre_text_example)
        self.assertEquals('Nvidia', resources['gpu'][0].vendor_id)
        self.assertEquals('K20 GPU Accelerator', resources['gpu'][0].model_name)
        self.assertEquals('Nvidia', resources['gpu'][1].vendor_id)
        self.assertEquals('K20 GPU Accelerator', resources['gpu'][1].model_name)
