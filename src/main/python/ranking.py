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

def _read_csv_first_line(file, execution_id):
    """
    Returns the line with the execution id if possible,
    empty line otherwise
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

def _execute_comparator(execution, endpoint, path, command):
    """
    It takes an execution object and calculates the 
    comparator provided by the self-adapation manager
    """
    pass
    