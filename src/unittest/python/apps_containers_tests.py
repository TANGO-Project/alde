# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: Roi Sucasas Font, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import unittest
import apps_containers


class AppsContaintersTests(unittest.TestCase):
    """
    Unit tests for the methods of apps_containers
    """

    """
    working path: resources (testBSC.zip, template, singularity image - if already created -) needed to
    run the application are located in the following path
    """
    WORKING_FOLDER = "/home/atos/tango/alde/src/main/resources/"

    SINGULARITY_IMG_NAME = "test2.img"
    SINGULARITY_DEF_NAME = "test2.def"
    APP_ZIP_PATH = "/home/atos/tango/alde/src/main/resources/testBSC.zip"
    TEMPLATE_ID = "tango_pgmodel_cuda75_v02"
    CREATE_IMG = False
    BUILD_COMMAND = "buildapp Matmul"
    RUN_COMMAND = ""
    APP_FOLDER_LOCATION = "/home/atos/tango/alde/src/main/resources/testBSC/."

    # TEMPLATES & IMG sizes
    TEMPLATES_DEF = {
        'ID_TEMPLATE_PGMODEL_CUDA7_5' : 'tango_pgmodel_cuda75_v02',
        'TEMPLATE_PGMODEL_CUDA7_5' : '/home/atos/tango/alde/src/main/resources/tango_pgmodel_cuda75_v02_template.txt',
        'SIZE_IMG_PGMODEL_CUDA7_5' : '4500'
    }

    def _test_load_config(self):
        """ Test that verifies the creation of a Singularity image containing a test program """

        apps_containers.set_templates_def(self.TEMPLATES_DEF)

        res = apps_containers.setup_sing_img(self.WORKING_FOLDER, self.SINGULARITY_IMG_NAME, self.SINGULARITY_DEF_NAME, self.APP_ZIP_PATH,
                             self.TEMPLATE_ID, self.CREATE_IMG, self.BUILD_COMMAND, self.RUN_COMMAND, self.APP_FOLDER_LOCATION)

        self.assertEquals(True, res)
