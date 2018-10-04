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
# Module that containds db queries
#

from models import db, Testbed

def get_slurm_online_testbeds():
    """
    It returns all the testbeds from the db that fulfill the following
    conditions:

        Testbed is on-line
        Testbed is of category slurm
    """

    return db.session.query(Testbed).filter(Testbed.on_line == True).filter(Testbed.category == Testbed.slurm_category).all()
