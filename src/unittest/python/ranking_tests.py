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
import os
import unittest.mock as mock
from testfixtures import LogCapture
from models import db, Execution, ExecutionConfiguration, Application, Testbed
from sqlalchemy_mapping_tests.mapping_tests import MappingTest

class RankingTests(MappingTest):
    """
    Unit tests for the ranking module
    """

    execution = None

    def setUp(self):
        """
        It creates the model objects and saves then in the database
        """
        super(RankingTests, self).setUp()

        self.execution = Execution()
        self.execution.slurm_sbatch_id = 2333

        execution_configuration = ExecutionConfiguration()
        execution_configuration.id = 22
        self.execution.execution_configuration = execution_configuration

        application = Application()
        application.name = "Matmul"
        execution_configuration.application = application

        testbed = Testbed("nova", True, "SLURM", "SSH", "pepito@ssh.com", [ "SINGULARITY" ] )
        execution_configuration.testbed = testbed

        db.session.add(testbed)
        db.session.add(application)
        db.session.add(execution_configuration)
        db.session.add(self.execution)
        db.session.commit()

    def test_read_csv_first_line(self):
        """
        It checks that it is possible to read the line with an specific exeuction id of a csv file
        """

        l = LogCapture() # we cature the logger

        file = 'Time_Ranking.csv'

        line = ranking._read_ranking_info(file, 7332)
        
        self.assertEqual('Matmul', line[0])
        self.assertEqual('5851', line[1])
        self.assertEqual('20', line[2])
        self.assertEqual('7332', line[3])
        self.assertEqual('20', line[4])

        # inexistent file test
        file = 'no_file.csv'

        line = ranking._read_ranking_info(file, 7332)
        self.assertEqual([], line)

        # Execution id does not exists
        file = 'Time_Ranking.csv'

        line = ranking._read_ranking_info(file, 11)
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
        
        ranking._execute_comparator(self.execution, 'endpoint', '/path')

        mock_shell.assert_called_with(os.path.join('/path','post_run_processing.sh'), 'endpoint', ['2333', 'Matmul', '22'])
    
    @mock.patch("ranking._read_ranking_info")
    @mock.patch("ranking._execute_comparator")
    def test_update_ranking_info_for_an_execution(self, mock_comparator, mock_read):
        """
        It evaluates the correct work of the module function:
        update_ranking_info_for_an_execution
        """
        mock_read.return_value = [ 'Matmul', '5851', '20', '2333', '22' ]
        
        ranking.update_ranking_info_for_an_execution(self.execution, '/path', 'file')

        execution = db.session.query(Execution).filter_by(id=self.execution.id).first()

        self.assertEqual(5851, execution.energy_output)
        self.assertEqual(20, execution.runtime_output)

        mock_comparator.assert_called_with(self.execution, 'pepito@ssh.com', '/path')
        mock_read.assert_called_with('file', 2333)