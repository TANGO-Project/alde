#!/usr/bin/env python
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information
#
# Unit tests for ranking.py file
#

import ranking
import unittest
from testfixtures import LogCapture

class RankingTests(unittest.TestCase):
    """
    Unit tests for the ranking module
    """

    def test_read_csv_first_line(self):
        """
        It checks that it is possible to read the first line of a csv file
        """

        l = LogCapture() # we cature the logger

        file = 'Time_Ranking.csv'

        line = ranking._read_csv_first_line(file)

        self.assertEqual('Matmul', line[0])
        self.assertEqual('5851', line[1])
        self.assertEqual('20', line[2])
        self.assertEqual('7332', line[3])
        self.assertEqual('20', line[4])

        # inexistent file test
        file = 'no_file.csv'

        line = ranking._read_csv_first_line(file)
        self.assertEqual([], line)

        l.check(
            ('root', 'ERROR', "Could not read file: " + file)
        )
        l.uninstall() # We uninstall the capture of the logger