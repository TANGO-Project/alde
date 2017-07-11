# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information

import json
from models import GPU

GPU_FILE = "gpu_cards_list.json"

def find_gpu_slurm(model_code_slurm):
    """
    This function will look at the internal json gpu inventory and look
    for the GPU that has the same "model_code_slurm" field and return a
    GPU object
    """

    with open(GPU_FILE) as data_file:
        gpus = json.load(data_file)

    gpu = next((gpu for gpu in gpus if gpu['model_code_slurm'] == model_code_slurm), None)

    if gpu:
        return GPU(vendor_id=gpu['vendor_id'], model_name=gpu['model_name'])
    else:
        return None
