#!/usr/bin/env python
# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

from model.base import db
from model.models import Testbed

def get_slurm_online_testbeds():
    """
    It returns all the testbeds from the db that fulfill the following
    conditions:

        Testbed is on-line
        Testbed is of category slurm
    """

    return db.session.query(Testbed).filter(Testbed.on_line == True).filter(Testbed.category == Testbed.slurm_category).all()
