# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information


import unittest
import slurm

class SlurmTests(unittest.TestCase):
    """
    Unittests of the functions used to interact with and slurm
    testbed
    """

    def test_parse_sinfo_partitions(self):
        """
        Check it is possible to parse the output of the slurm
        sinfo -a
        command
        """

        command_output = """PARTITION    AVAIL  TIMELIMIT  NODES  STATE NODELIST
bullx           up   infinite      1  drain nd15
bullx           up   infinite      9   idle nd[10-14,16-19]
partners*       up    8:00:00      1  drain nd15
partners*       up    8:00:00      9   idle nd[10-14,16-19]
gpus            up   infinite      2 drain* nd[20-21]
gpus            up   infinite      1   idle nd22
gpu2075         up   infinite      1 maint* nd23
B510_2.2GHz     up   infinite      2 maint* nd[36-37]
B510_2.2GHz     up   infinite      2   idle nd[38-39]
B510_2.6GHz     up   infinite      2 maint* nd[32-33]
B510_2.6GHz     up   infinite      1  maint nd31
B510_2.6GHz     up   infinite      9   idle nd[24-26,28-30,40-41,43]
B510_2.6GHz     up   infinite      2   down nd[27,42]
B515k20x        up   infinite      2 drain* nd[44-45]
B515xeon-phi    up   infinite      2 drain* nd[46-47]
B520            up   infinite      1 drain* nd56
B520            up   infinite      9  drain nd[57-65]
bullion         up   infinite      1  maint nd76
bullion_S       up   infinite      1  alloc nd80"""

        output = slurm.parse_sinfo_partitions(command_output)

        # We verify the output
        self.assertEquals(58,len(output))

        for node in output:
            print(node)
