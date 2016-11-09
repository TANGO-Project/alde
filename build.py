# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information
#

from pybuilder.core import init, use_plugin

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.coverage")
use_plugin("python.install_dependencies")
use_plugin("python.distutils")
use_plugin("python.sonarqube")

default_task = "publish"

# SonarQube configuration:
sonarqube_project_name = "tango-alde"
sonarqube_project_key = "ce9b5211cc48e2ca6ac94406eb8fe0a0f31eed06"

@init
def initialize(project):
    project.build_depends_on('mockito')