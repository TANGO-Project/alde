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
from model.base import db # pragma: no cover

def load_config():
    config = configparser.ConfigParser()
    config.read('alde_configuration.ini')
    print(config.sections())
    default = config['DEFAULT']
    print(default)

    conf = {
        'SQL_LITE_URL' : default['SQL_LITE_URL'],
        'PORT' : default['PORT']
    }

    return conf

#conf = load_config() # pragma: no cover
#app = alde.create_app_v1(conf['SQL_LITE_URL'], conf['PORT']) # pragma: no cover

# We start the Flask loop
#db.create_all() # pragma: no cover
# app.run(use_reloader=False)
