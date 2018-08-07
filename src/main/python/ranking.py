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

def _read_csv_first_line(file):
    """
    Returns a file first line if possible,
    empty line otherwise
    """
    
    line = []
    
    try :
        with open(file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            first_line = next(spamreader)
            line = [x.strip() for x in first_line]
    
    except IOError:
        logging.error("Could not read file: " + file)
        
    return line