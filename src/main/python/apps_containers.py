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
# Module that creates the sigularity containers
#
import sys
import subprocess
import os
import zipfile


# TEMPLATES & IMG sizes
templates_def = {
    'ID_TEMPLATE_PGMODEL_CUDA7_5' : 'tango_pgmodel_cuda75_v02',
    'TEMPLATE_PGMODEL_CUDA7_5' : '/home/atos/tango/alde/src/main/resources/tango_pgmodel_cuda75_v02_template.txt',
    'SIZE_IMG_PGMODEL_CUDA7_5' : '4500'
}


# #########################################################
# Set templates paths / properties
# 	tdef .....
# ########################################################
def set_templates_def(tdef):
    templates_def = tdef
    print("[set_templates_def] ID_TEMPLATE_PGMODEL_CUDA7_5=" + templates_def['ID_TEMPLATE_PGMODEL_CUDA7_5'])
    print("[set_templates_def] TEMPLATE_PGMODEL_CUDA7_5=" + templates_def['TEMPLATE_PGMODEL_CUDA7_5'])
    print("[set_templates_def] SIZE_IMG_PGMODEL_CUDA7_5=" + templates_def['SIZE_IMG_PGMODEL_CUDA7_5'])


# #########################################################
# Creates a zip file
# 	zfile ..... "testBSC.zip"
# 	folder .... "testBSC"
# ########################################################
def zip_file(zfile, folder):
    print("[zip_file] Zip folder [" + folder + "] into [" + zfile + "] ...")
    try:
        zf = zipfile.ZipFile(zfile, "w")
        for dirname, subdirs, files in os.walk(folder):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()
        return True
    except Exception as e:
        print("[zip_file] ERROR: " + e)
        return False


# #########################################################
# Unzip file
# 	zfile ..... "testBSC.zip"
# ########################################################
def unzip_file(zfile, destpath):
    print("[unzip_file] Unzip file [" + zfile + "] ...")
    try:
        zip_ref = zipfile.ZipFile(zfile, 'r')
        zip_ref.extractall(destpath + ".")
        zip_ref.close()
        return True
    except Exception as e:
        print("[unzip_file] ERROR: " + e)
        return False


# ########################################################
# Creates a file
# 	f ..... "boot.def"
# ########################################################
def create_file(f):
    print("[create_file] Creating new file [" + f + "]...")
    try:
        file = open(f,'w')   # Trying to create a new file or open one
        file.close()
        return True
    except Exception as e:
        print("[create_file] ERROR: " + e)
        return False


# ########################################################
# Creates a singularity .def file based on a template
#	template ....... 'tango_pgmodel_cuda75_v02'
#	appfolder ...... "testBSC"
#	folderlocation
#	bcommand
#	rcommand
#	filedest ....... 'test_template_1.def'
# ########################################################
def create_sing_boot_script(template, appfolder, folderlocation, bcommand, rcommand, filedest):
    print("[create_sing_boot_script] Creating new template [" + template + "]...")
    try:
        replacements = {'#APP_FOLDER#':appfolder, '#FOLDER_LOCATION#':folderlocation, '#BUILD_COMMAND#':bcommand, '#RUN_COMMAND#':rcommand}
        boottemplate = ''

        if template == templates_def['ID_TEMPLATE_PGMODEL_CUDA7_5']:
            boottemplate = templates_def['TEMPLATE_PGMODEL_CUDA7_5']
        else:
            boottemplate = ''

        if boottemplate != '':
            with open(boottemplate) as infile, open(filedest, 'w') as outfile:
                for line in infile:
                    for src, target in replacements.items():
                        line = line.replace(src, target)
                    outfile.write(line)
            return True
        else:
            print("[create_sing_boot_script] Something went wrong!")
    except Exception as e:
        print("[create_sing_boot_script] ERROR: " + e)
    return False


# ########################################################
# Creates a singularity .def file based on a template
#   workingFolder ......... "/home/atos/tango/alde/src/main/resources/"
#   singularityImgName .... "test2.img" (used with 'workingFolder' in order to get the full path)
#   singularityDefName .... "test2.def" (used with 'workingFolder' in order to get the full path)
#   appZipPath
#   templateId
#   createSingularityImg
#   buildCommand
#   runCommand
#   appFolderLocation
# ########################################################
def setup_sing_img(workingFolder, singularityImgName, singularityDefName, appZipPath, templateId, createSingularityImg,
                   buildCommand, runCommand, appFolderLocation):
    print("[setup_sing_img] ...")
    singularityImgPath = workingFolder + singularityImgName
    singularityDefPath = workingFolder + singularityDefName
    print("[setup_sing_img] singularityImgPath=[" + singularityImgPath + "], singularityDefPath=[" + singularityDefPath + "]")

    try:
        if createSingularityImg:
            if templateId == templates_def['ID_TEMPLATE_PGMODEL_CUDA7_5']:
                os.system("sudo singularity create -s " + templates_def['SIZE_IMG_PGMODEL_CUDA7_5'] + " " + singularityImgPath)
            else:
                print("[setup_sing_img] template " + templateId + " not defined")

        if unzip_file(appZipPath, workingFolder):
            if create_sing_boot_script(templateId, workingFolder, appFolderLocation, buildCommand, runCommand, singularityDefPath):
                os.system("sudo singularity bootstrap " + singularityImgPath + " " + singularityDefPath)
                os.system("sudo singularity run " + singularityImgPath)
                return True
    except Exception as e:
        print("[setup_sing_img] ERROR: " + e)
    return False

# ##############################################################################
# execute / test:

# workingFolder = "/home/atos/tango/alde/src/main/resources/"
# singularityImgName = "test2.img"
# singularityDefName = "test2.def"
# appZipPath = "/home/atos/tango/alde/src/main/resources/testBSC.zip"
# templateId = "tango_pgmodel_cuda75_v02"
# createSingularityImg = False
# buildCommand = "buildapp Matmul"
# runCommand = ""
# appFolderLocation = "/home/atos/tango/alde/src/main/resources/testBSC/."

# set_templates_def({
#     'ID_TEMPLATE_PGMODEL_CUDA7_5' : 'tango_pgmodel_cuda75_v02',
#     'TEMPLATE_PGMODEL_CUDA7_5' : '/home/atos/tango/alde/src/main/resources/tango_pgmodel_cuda75_v02_template.txt',
#     'SIZE_IMG_PGMODEL_CUDA7_5' : '4500'
# })

# setup_sing_img(workingFolder, singularityImgName, singularityDefName, appZipPath,templateId, createSingularityImg,
#                buildCommand, runCommand, appFolderLocation)
