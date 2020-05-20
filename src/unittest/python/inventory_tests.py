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
# Unit tests that checks ALDE GPU database reading.
#

import unittest
import inventory

class InventoryTests(unittest.TestCase):
    """
    Verifies the correct work of all the functions inside the inventory
    module, responsible of parsing all json internal inventory information
    to complement the GPU and other hardware information of components
    in nodes used by ALDE
    """

    def test_find_gpu_slurm(self):
        """
        This test verifies that we can find the right GPU from a json-list
        stored in a file
        """
        inventory.GPU_FILE = "gpu_cards_list.json"

        gpu = inventory.find_gpu_slurm("tesla2075")
        self.assertEquals("Nvidia", gpu.vendor_id)
        self.assertEquals("Nvidia TESLA C2075", gpu.model_name)

        gpu = inventory.find_gpu_slurm("xxxxx")
        self.assertIsNone(gpu)


    def test_find_gpu(self):
        """Test the generic find function"""
        inventory.GPU_FILE = "gpu_cards_list.json"

        gpu = inventory.find_gpu("GeForce GTX 1080 Ti", inventory.FIELD_MODEL_NAME)
        self.assertEqual("Nvidia", gpu.vendor_id)
        self.assertEqual("GeForce GTX 1080 Ti", gpu.model_name)

        gpu = inventory.find_gpu("xxxxx", inventory.FIELD_CODE_SLURM)
        self.assertIsNone(gpu)
        