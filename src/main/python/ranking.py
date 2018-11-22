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
# Module that stores all the ranking of different configurations
#

import csv
import logging
import shell
import os
from models import db

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

    shell.execute_command(os.path.join(path,'post_run_processing.sh'), endpoint, [
        str(execution.slurm_sbatch_id),
        execution.execution_configuration.application.name,
        str(execution.execution_configuration.id)
    ])

def update_ranking_info_for_an_execution(execution, path, file):
    """
    It updates the ranking information for an execution
    Executing in a first step the comparator.
    """
    
    endpoint = execution.execution_configuration.testbed.endpoint

    _execute_comparator(execution, endpoint, path)

    ranking = _read_ranking_info(file, execution.slurm_sbatch_id)

    if len(ranking) > 3 :

        execution.energy_output = ranking[1]
        execution.runtime_output = ranking[2]

    db.session.commit()