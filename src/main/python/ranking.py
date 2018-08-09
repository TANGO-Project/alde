#!/usr/bin/env python
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information
#
# It stores all the logic to read and create the ranking files
# for a given execution. Using the commands provided by the
# TANGO Self-Adaptation Manager
#

import csv
import logging
import shell

def _read_ranking_info(file, execution_id):
    """
    Returns the line with the execution id if possible,
    empty line otherwise
    ./post_run_processing.sh 7332 Matmul 20
    """
    try :
        with open(file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            
            for line_in_file in spamreader:
                line = [x.strip() for x in line_in_file] # We remove the white space

                if int(line[3]) == execution_id :
                    return line
    
    except IOError:
        logging.error("Could not read file: " + file)
        
    return []

def _execute_comparator(execution, endpoint, path):
    """
    It takes an execution object and calculates the 
    comparator provided by the self-adapation manager
    """

    shell.execute_command(path + '/post_run_processing.sh', endpoint, [
        str(execution.slurm_sbatch_id),
        execution.execution_configuration.application.name,
        str(execution.execution_configuration.id)
    ])

def update_ranking_info_for_an_execution(execution, path, file):
    """
    It updates the ranking information for an execution
    Executing in a first step the comparator.
    """
    
    pass