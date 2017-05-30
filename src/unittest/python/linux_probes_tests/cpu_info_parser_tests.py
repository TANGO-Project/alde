# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information


import unittest
import unittest.mock as mock
import shell
import subprocess
import linux_probes.cpu_info_parser as parser
from model.models import Node, Testbed
from testfixtures import LogCapture

class CpuInfoParserTests(unittest.TestCase):
    """Verifies the correct work of the funcions for parsing cpu info information"""

    command_output=b'processor\t: 0\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 26\nmodel name\t: Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz\nstepping\t: 5\nmicrocode\t: 17\ncpu MHz\t\t: 2267.000\ncache size\t: 8192 KB\nphysical id\t: 0\nsiblings\t: 4\ncore id\t\t: 0\ncpu cores\t: 4\napicid\t\t: 0\ninitial apicid\t: 0\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 11\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid\nbogomips\t: 4533.65\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 40 bits physical, 48 bits virtual\npower management:\n\nprocessor\t: 1\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 26\nmodel name\t: Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz\nstepping\t: 5\nmicrocode\t: 17\ncpu MHz\t\t: 2267.000\ncache size\t: 8192 KB\nphysical id\t: 0\nsiblings\t: 4\ncore id\t\t: 1\ncpu cores\t: 4\napicid\t\t: 2\ninitial apicid\t: 2\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 11\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid\nbogomips\t: 4533.65\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 40 bits physical, 48 bits virtual\npower management:\n\nprocessor\t: 2\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 26\nmodel name\t: Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz\nstepping\t: 5\nmicrocode\t: 17\ncpu MHz\t\t: 2267.000\ncache size\t: 8192 KB\nphysical id\t: 0\nsiblings\t: 4\ncore id\t\t: 2\ncpu cores\t: 4\napicid\t\t: 4\ninitial apicid\t: 4\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 11\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid\nbogomips\t: 4533.65\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 40 bits physical, 48 bits virtual\npower management:\n\nprocessor\t: 3\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 26\nmodel name\t: Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz\nstepping\t: 5\nmicrocode\t: 17\ncpu MHz\t\t: 2267.000\ncache size\t: 8192 KB\nphysical id\t: 0\nsiblings\t: 4\ncore id\t\t: 3\ncpu cores\t: 4\napicid\t\t: 6\ninitial apicid\t: 6\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 11\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid\nbogomips\t: 4533.65\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 40 bits physical, 48 bits virtual\npower management:\n\nprocessor\t: 4\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 26\nmodel name\t: Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz\nstepping\t: 5\nmicrocode\t: 17\ncpu MHz\t\t: 2267.000\ncache size\t: 8192 KB\nphysical id\t: 1\nsiblings\t: 4\ncore id\t\t: 0\ncpu cores\t: 4\napicid\t\t: 16\ninitial apicid\t: 16\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 11\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid\nbogomips\t: 4532.67\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 40 bits physical, 48 bits virtual\npower management:\n\nprocessor\t: 5\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 26\nmodel name\t: Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz\nstepping\t: 5\nmicrocode\t: 17\ncpu MHz\t\t: 2267.000\ncache size\t: 8192 KB\nphysical id\t: 1\nsiblings\t: 4\ncore id\t\t: 1\ncpu cores\t: 4\napicid\t\t: 18\ninitial apicid\t: 18\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 11\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid\nbogomips\t: 4532.67\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 40 bits physical, 48 bits virtual\npower management:\n\nprocessor\t: 6\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 26\nmodel name\t: Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz\nstepping\t: 5\nmicrocode\t: 17\ncpu MHz\t\t: 2267.000\ncache size\t: 8192 KB\nphysical id\t: 1\nsiblings\t: 4\ncore id\t\t: 2\ncpu cores\t: 4\napicid\t\t: 20\ninitial apicid\t: 20\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 11\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid\nbogomips\t: 4532.67\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 40 bits physical, 48 bits virtual\npower management:\n\nprocessor\t: 7\nvendor_id\t: GenuineIntel\ncpu family\t: 6\nmodel\t\t: 26\nmodel name\t: Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz\nstepping\t: 5\nmicrocode\t: 17\ncpu MHz\t\t: 2267.000\ncache size\t: 8192 KB\nphysical id\t: 1\nsiblings\t: 4\ncore id\t\t: 3\ncpu cores\t: 4\napicid\t\t: 22\ninitial apicid\t: 22\nfpu\t\t: yes\nfpu_exception\t: yes\ncpuid level\t: 11\nwp\t\t: yes\nflags\t\t: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid\nbogomips\t: 4532.67\nclflush size\t: 64\ncache_alignment\t: 64\naddress sizes\t: 40 bits physical, 48 bits virtual\npower management:\n\n'

    def test_command_output(self):
        """ It verifies that the function parse_cpu_info works as expected"""

        cpus = parser.parse_cpu_info(self.command_output)

        self.assertEquals(8, len(cpus))

        i = 0
        for cpu in cpus:
            self.assertEquals('GenuineIntel', cpu.vendor_id)
            self.assertEquals('Intel(R) Xeon(R) CPU           E5520  @ 2.27GHz',
                               cpu.model_name)
            self.assertEquals('x86_64', cpu.arch)
            self.assertEquals('26', cpu.model)
            self.assertEquals('2267.000', cpu.speed)
            self.assertTrue(cpu.fpu)
            self.assertEquals(4, cpu.cores)
            self.assertEquals('8192 KB', cpu.cache)
            self.assertEquals('fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx rdtscp lm constant_tsc arch_perfmon pebs bts rep_good xtopology nonstop_tsc aperfmperf pni dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm dca sse4_1 sse4_2 popcnt lahf_lm ida dts tpr_shadow vnmi flexpriority ept vpid',
                               cpu.flags)
            self.assertEquals(i // 4, cpu.physical_id)
            self.assertEquals(4, cpu.siblings)
            self.assertEquals(5, cpu.stepping)
            self.assertEquals('17', cpu.microcode)
            self.assertTrue(cpu.fpu_exception)
            self.assertTrue(cpu.wp)
            self.assertEquals('453', cpu.bogomips[0:3])
            i = i + 1

    @mock.patch("shell.execute_command")
    def test_get_cpuinfo_node(self, mock_shell):
        """
        It verfies that given a testbed it is possible to get the cpuinfo
        information of the node.
        """

        l = LogCapture() # we cature the logger

        # When the testbed is local
        testbed = Testbed("name1",
                            True,
                            Testbed.slurm_category,
                            Testbed.protocol_local,
                            "user@server",
                            ['slurm'])

        node_1 = Node("node_1", True) # We add some nodes to Testbed_1
        node_2 = Node("node_2", True)
        testbed.nodes = [ node_1, node_2]
        node_1.disabled = True
        node_3 = Node("node_3", True)

        # When the node does not belong to the testbed it should return empty list
        cpus = parser.get_cpuinfo_node(testbed, node_3)

        self.assertEquals(0, len(cpus))

        # When the node is there, we have to get double CPU info
        mock_shell.return_value = self.command_output

        cpus = parser.get_cpuinfo_node(testbed, node_2)

        self.assertEquals(8, len(cpus))
        mock_shell.assert_called_with(command="ssh",
                                      params=["node_2", "'cat", "/proc/cpuinfo'"])
        self.assertEqual(mock_shell.call_count, 1)

        # When the node is dissabled it should return an empty list
        cpus = parser.get_cpuinfo_node(testbed, node_1)

        self.assertEquals(0, len(cpus))
        self.assertEqual(mock_shell.call_count, 1)

        # When the testbed is using ssh protocol
        testbed = Testbed("name1",
                            True,
                            Testbed.slurm_category,
                            Testbed.protocol_ssh,
                            "user@server",
                            ['slurm'])
        testbed.nodes = [node_2]

        mock_shell.return_value = self.command_output

        cpus = parser.get_cpuinfo_node(testbed, node_2)

        self.assertEquals(8, len(cpus))
        mock_shell.assert_called_with(command="ssh",
                                      server=testbed.endpoint,
                                      params=["node_2", "'cat", "/proc/cpuinfo'"])
        self.assertEqual(mock_shell.call_count, 2)

        # We simulate what happens if we get an exception executing the command
        error = subprocess.CalledProcessError(returncode=255, cmd="ls")
        mock_shell.side_effect = error

        cpus = parser.get_cpuinfo_node(testbed, node_2)

        self.assertEquals(0, len(cpus))
        self.assertEqual(mock_shell.call_count, 3)

        # When the testbed has an unknown protocol
        testbed = Testbed("name1",
                            True,
                            Testbed.slurm_category,
                            "xxx",
                            "user@server",
                            ['slurm'])
        testbed.nodes = [node_2]

        cpus = parser.get_cpuinfo_node(testbed, node_2)

        self.assertEquals(0, len(cpus))
        self.assertEqual(mock_shell.call_count, 3)

        # We verify that we raised the right errors
        # Checking that we are logging the correct messages
        l.check(
            ('root', 'ERROR', 'Exception trying to get the node cpu info'),
            ('root', 'INFO', 'Tesbed protocol: xxx not supported to get node information')
            )
        l.uninstall() # We uninstall the capture of the logger
