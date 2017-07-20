# Application Lifecycle Deployment Engine (ALDE)

&copy; Atos Spain S.A. 2016

Application Lifecycle Deployment Engine (ALDE) is a component of the European Project TANGO (http://tango-project.eu ).

ALDE is distributed under a [Apache License, version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

## Description

ALDE is responsible for the workload scheduling and the management of the application life-cycle while it is executed. ALDE will take the application source code, packetize for different heterogenous architectures configurations and, if possible, deploy it via a TANGO Device Supervisor and manage the application execution. 

More in detail each one of the previous steps:

* **Compilation** - ALDE is able to compile the application in different configurations depending of the selected heterogenous architectures. The result will be a set of binaries optimal compiled for specific hardware architectures.
* **Packetization** - ALDE, once the application has been compiled, can packetize it. For the moment it only supports typical tar.gz files and [Docker](https://www.docker.com/) and [Singularity](http://singularity.lbl.gov/) containers.
* **Deployment** - ALDE is able to automatically deploy an application into a TANGO compatible Device Supervisor. It will launch the execution and monitor it. It will also support adaptations interactions if used in combination with the [TANGO Self-Adaptation Manager](https://github.com/TANGO-Project/self-adaptation-manager).

## Installation Guide

This guide it is divided into two different guides, one specific to create an environment for development and another one to just run and use ALDE.

### Installation for development

#### Requirements

To develop for ALDE we need to install two pieces of software:

* [Python 3.6 or higher](https://www.python.org).
* [Virtualenv](https://virtualenv.pypa.io/en/stable/).

#### Installation and configuration procedure

To develop ALDE it is necessary to create a [Python Virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) (depending on your installation of Python pip3 command can be called pip):


```
$ pip3 install virtualenv
Collecting virtualenv
  Downloading virtualenv-15.0.3-py2.py3-none-any.whl (3.5MB)
    100% |████████████████████████████████| 3.5MB 398kB/s
Installing collected packages: virtualenv
Successfully installed virtualenv-15.0.3
```

After that, you need to create a virtualenv for you to develop:

```
$ virtualenv venv
Using base prefix '/Library/Frameworks/Python.framework/Versions/3.5'
New python executable in /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/venv/bin/python3.5
Also creating executable in /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/venv/bin/python
Installing setuptools, pip, wheel...done.
```

Now it time to install PyBuilder:

* First we activate the virtualenv:

```
$ source venv/bin/activate
```

* Now we install PyBuilder using Pip:

```
$ pip install pybuilder
Collecting pybuilder
  Using cached PyBuilder-0.11.9.tar.gz
Requirement already satisfied: pip>=7.0 in ./venv/lib/python3.5/site-packages (from pybuilder)
Collecting tblib (from pybuilder)
  Using cached tblib-1.3.0-py2.py3-none-any.whl
Requirement already satisfied: wheel in ./venv/lib/python3.5/site-packages (from pybuilder)
Building wheels for collected packages: pybuilder
  Running setup.py bdist_wheel for pybuilder ... done
  Stored in directory: /Users/davidgp/Library/Caches/pip/wheels/04/9c/b3/d2d2194e8911818abdfa1c3c47501a64602714415af28d8da8
Successfully built pybuilder
Installing collected packages: tblib, pybuilder
Successfully installed pybuilder-0.11.9 tblib-1.3.0
(venv)
```

Now it is possible to compile the project:

* Install first the dependencies:

```
$ pyb install_dependencies
PyBuilder version 0.11.9
Build started at 2016-11-11 14:55:00
------------------------------------------------------------
[INFO]  Building alde version 1.0.dev0
[INFO]  Executing build in /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde
[INFO]  Going to execute task install_dependencies
[INFO]  Installing all dependencies
[INFO]  Processing batch dependency 'mockito'
------------------------------------------------------------
BUILD SUCCESSFUL
------------------------------------------------------------
Build Summary
             Project: alde
             Version: 1.0.dev0
      Base directory: /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde
        Environments:
               Tasks: install_dependencies [9623 ms]
Build finished at 2016-11-11 14:55:10
Build took 9 seconds (9637 ms)
```

* Now you can build the project (if you are using Windows, probably the coverage task is going to fail)

```
$ pyb
PyBuilder version 0.11.9
Build started at 2016-11-11 14:57:03
------------------------------------------------------------
[INFO]  Building alde version 1.0.dev0
[INFO]  Executing build in /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde
[INFO]  Going to execute task publish
[INFO]  Installing plugin dependency coverage
[INFO]  Installing plugin dependency unittest-xml-reporting
[INFO]  Running unit tests
[INFO]  Executing unit tests from Python modules in /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/src/unittest/python
[INFO]  Executed 1 unit tests
[INFO]  All unit tests passed.
[INFO]  Building distribution in /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/target/dist/alde-1.0.dev0
[INFO]  Copying scripts to /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/target/dist/alde-1.0.dev0/scripts
[INFO]  Writing setup.py as /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/target/dist/alde-1.0.dev0/setup.py
[INFO]  Collecting coverage information
[WARN]  coverage_branch_threshold_warn is 0 and branch coverage will not be checked
[WARN]  coverage_branch_partial_threshold_warn is 0 and partial branch coverage will not be checked
[INFO]  Running unit tests
[INFO]  Executing unit tests from Python modules in /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/src/unittest/python
[INFO]  Executed 1 unit tests
[INFO]  All unit tests passed.
[WARN]  Module '__init__' was not imported by the covered tests
[INFO]  Overall coverage is 94%
[INFO]  Overall coverage branch coverage is 100%
[INFO]  Overall coverage partial branch coverage is 100%
[INFO]  Building binary distribution in /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/target/dist/alde-1.0.dev0
------------------------------------------------------------
BUILD SUCCESSFUL
------------------------------------------------------------
Build Summary
             Project: alde
             Version: 1.0.dev0
      Base directory: /Users/davidgp/Documents/trabajo/TANGO/repositorios/alde
        Environments:
               Tasks: prepare [2407 ms] compile_sources [0 ms] run_unit_tests [40 ms] package [3 ms] run_integration_tests [0 ms] verify [134 ms] publish [616 ms]
Build finished at 2016-11-11 14:57:06
Build took 3 seconds (3219 ms)
```

Done!

Now, remember, each time you need to start to develop, initalize the virtualenv:

```
$ source venv/bin/activate
```


#### Tests with Singularity

1. Install Singularity - [View doc](SingularityTests.md)

#### Build status from Travis-CI

[![Build Status](https://travis-ci.org/TANGO-Project/alde.svg?branch=master)](https://travis-ci.org/TANGO-Project/alde)

#### SonarQube reports:

SonarQube ( http://www.sonarqube.org/ ) reports for this project are available at: https://sonarqube.com/dashboard?id=tango%3Aalde

### Installation for running the service

In this case, we are going to detail how to run the application directly using Python. It is possible to run it behind a proxy or webserver, to do so, please, check [this guides](http://flask.pocoo.org/docs/0.12/deploying/).

#### Configuring the service

ALDE employs a [SQLite](https://www.sqlite.org/) database server that needs to be configured together with the port were the service it is going to be listen. That configuration can be done editing the file alde_configuration.ini that contains these two variables:

```dosini
[DEFAULT]
SQL_LITE_URL = sqlite:////tmp/test.db
PORT = 5000
```

To install it, it is necessary to execute the following command:

```
python setup.py install
```

To launch the service we need to execute:

```
$ python app.py 
2017-07-18 09:16:02,812 root         INFO     Loading configuration
[]
<Section: DEFAULT>
2017-07-18 09:16:02,813 root         INFO     Starting ALDE
/Users/davidgp/Documents/trabajo/TANGO/repositorios/alde/venv/lib/python3.6/site-packages/flask_sqlalchemy/__init__.py:839: FSADeprecationWarning: SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled by default in the future.  Set it to True or False to suppress this warning.
  'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and '
2017-07-18 09:16:02,937 apscheduler.scheduler INFO     Adding job tentatively -- it will be properly scheduled when the scheduler starts
2017-07-18 09:16:02,937 apscheduler.scheduler INFO     Adding job tentatively -- it will be properly scheduled when the scheduler starts
2017-07-18 09:16:02,938 apscheduler.scheduler INFO     Adding job tentatively -- it will be properly scheduled when the scheduler starts
2017-07-18 09:16:02,940 apscheduler.scheduler INFO     Added job "check_nodes_in_db_for_on_line_testbeds" to job store "default"
2017-07-18 09:16:02,940 apscheduler.scheduler INFO     Added job "update_node_info" to job store "default"
2017-07-18 09:16:02,940 apscheduler.scheduler INFO     Added job "update_cpu_node_info" to job store "default"
2017-07-18 09:16:02,940 apscheduler.scheduler INFO     Scheduler started
2017-07-18 09:16:02,986 werkzeug     INFO      * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

After it we could verify it works just by execution the following (in this example we are using [Curl](https://curl.haxx.se/) but you could use another REST/http client):

```
$ curl localhost:5000/api/v1/testbeds
{
  "num_results": 0, 
  "objects": [], 
  "page": 1, 
  "total_pages": 0
}

```

## Usage Guide

Although a CLI client is planned, for the moment ALDE offers a REST interface.

### REST API documentation

The rest api is fully documented here: ( https://jsapi.apiary.io/previews/applicationlifecycledeploymentengine/reference/0/testbed )

### Example scenarios

Adding a new SLURM type testbed that you can connect via SSH protocol

```
curl localhost:5000/api/v1/testbeds -X POST -H'Content-type: application/json' -d'{ "name": "slurm_testbed", "on_line": true, "category": "SLURM", "protocol": "SSH", "endpoint": "user@ssh.com"}'
```

## Relation to other TANGO components

ALDE can be used as an standalone tool in TANGO, it will allow to compile application for different targeted heterogenous architectures in an optimize way and with different configurations of heterogenous devices, but its fully potential it is with other TANGO components:

* **Programming model and IDE tools** - TANGO Programming Model can connect with ALDE to submit the code for compilation and packetization. Also it could be intereact with ALDE to submit the application directly to a TANGO compatible device supervisor.
* **Device Supervisor** - ALDE can interact with a on-line testbed that has installed a TANGO device supervisor on it. This will allow to automatically deploy diferent configurations of the application and execute it, monitoring the execution and extract back the results.
* **Self-Adaptation Manager** - ALDE will provide intefaces for the Self-Adaptation Manager to change the configuration of an application to optimize its execution in a TANGO compatible testbed.
