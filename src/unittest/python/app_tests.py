#
# Copyright 2018 Atos Research and Innovation
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# https://www.gnu.org/licenses/agpl-3.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
# 
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Unit tests that checks ALDE Flask integration
#

import unittest
from app import load_config

class AppTests(unittest.TestCase):
    """
    Unit tests for the methods of the main app
    """

    def test_load_config(self):
        """ Test that verifies the app loads the right config """

        conf = load_config()

        self.assertEquals('sqlite:////tmp/test.db', conf['SQL_LITE_URL'])
        self.assertEquals('5000', conf['PORT'])
        self.assertEquals('/tmp', conf['APP_UPLOAD_FOLDER'])
        self.assertEquals('/tmp', conf['APP_PROFILE_FOLDER'])
        self.assertEquals(["RIGID", "MOULDABLE", "CHECKPOINTABLE", "MALLEABLE"], conf['APP_TYPES'])
        self.assertEquals('/tmp/comparator', conf['COMPARATOR_PATH'])
        self.assertEquals('comparator_file.csv', conf['COMPARATOR_FILE'])
