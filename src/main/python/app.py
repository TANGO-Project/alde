#!/usr/bin/env python
# Builder script for the Application Lifecycle Deployment Engine
#
# This is being developed for the TANGO Project: http://tango-project.eu
#
# Copyright: David García Pérez, Atos Research and Innovation, 2016.
#
# This code is licensed under an Apache 2.0 license. Please, refer to the LICENSE.TXT file for more information


# Main ALDE Falsk start app...

import configparser
import alde # pragma: no cover
import logging # pragma: no cover
import file_upload.upload as upload
from logging.config import fileConfig # pragma: no cover
from models import db # pragma: no cover

# Loading logger configuration
fileConfig('logging_config.ini') # pragma: no cover
logger = logging.getLogger() # pragma: no cover

def load_config():
    """
    Functions that loads ALDE configuration from file
    It is specting a file alde_configuration.ini in the same location
    than the main executable
    """

    logger.info("Loading configuration")
    config = configparser.ConfigParser()
    config.read('alde_configuration.ini')
    default = config['DEFAULT']
    print(default)
    app_types = [e.strip() for e in default['APP_TYPES'].split(',')]

    conf = {
        'SQL_LITE_URL' : default['SQL_LITE_URL'],
        'PORT' : default['PORT'],
        'APP_UPLOAD_FOLDER' : default['APP_UPLOAD_FOLDER'],
        'APP_PROFILE_FOLDER' : default['APP_PROFILE_FOLDER'],
        'APP_TYPES' : app_types
    }

    return conf

def main(): # pragma: no cover
    """
    Main function that starts the ALDE Flask Service
    """

    conf = load_config() # pragma: no cover

    logger.info("Starting ALDE") # pragma: no cover
    app = alde.create_app_v1(conf['SQL_LITE_URL'], conf['PORT'], conf['APP_UPLOAD_FOLDER'], conf['APP_PROFILE_FOLDER'], conf['APP_TYPES']) # pragma: no cover

    # We start the Flask loop
    db.create_all() # pragma: no cover

    # We register the upload url
    upload_prefix = alde.url_prefix_v1 + "/upload"
    app.register_blueprint(upload.upload_blueprint, url_prefix=upload_prefix)

    app.run(use_reloader=False)

if __name__ == '__main__':
    main()
