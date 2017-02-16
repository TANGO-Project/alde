# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

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
        inventory.GPU_FILE = "./src/main/python/gpu_cards_list.json"

        gpu = inventory.find_gpu_slurm("tesla2075")
        self.assertEquals("Nvidia", gpu.vendor_id)
        self.assertEquals("Nvidia TESLA C2075", gpu.model_name)

        gpu = inventory.find_gpu_slurm("xxxxx")
        self.assertIsNone(gpu)
