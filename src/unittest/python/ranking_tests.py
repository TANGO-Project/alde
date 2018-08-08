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
import shell
import unittest.mock as mock
from testfixtures import LogCapture
from models import Execution, ExecutionConfiguration, Application

class RankingTests(unittest.TestCase):
    """
    Unit tests for the ranking module
    """

    def test_read_csv_first_line(self):
        """
        It checks that it is possible to read the line with an specific exeuction id of a csv file
        """

        l = LogCapture() # we cature the logger

        file = 'Time_Ranking.csv'

        line = ranking._read_csv_first_line(file, 7332)

        self.assertEqual('Matmul', line[0])
        self.assertEqual('5851', line[1])
        self.assertEqual('20', line[2])
        self.assertEqual('7332', line[3])
        self.assertEqual('20', line[4])

        # inexistent file test
        file = 'no_file.csv'

        line = ranking._read_csv_first_line(file, 7332)
        self.assertEqual([], line)

        # Execution id does not exists
        file = 'Time_Ranking.csv'

        line = ranking._read_csv_first_line(file, 11)
        self.assertEqual([], line)

        l.check(
            ('root', 'ERROR', "Could not read file: no_file.csv")
        )
        l.uninstall() # We uninstall the capture of the logger
    
    @mock.patch("shell.execute_command")
    def test_execute_comparator(self, mock_shell):
        """
        It evaluates the the comparator command is executed as expected
        and the execution values are added

        ./post_run_processing.sh 7332 Matmul 20
        """

        execution = Execution()
        execution.slurm_sbatch_id = 2333

        execution_configuration = ExecutionConfiguration()
        execution_configuration.id = 22
        execution.execution_configuration = execution_configuration

        application = Application()
        application.name = "Matmul"
        execution_configuration.application = application
        
        ranking._execute_comparator(execution, 'endpoint', '/path', 'command')

        mock_shell.assert_called_with('/path/command', 'endpoint', [])