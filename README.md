# Malware Analysis and Storage System

## Introduction

The Malware Analysis and Storage System (MASS) is a joint research project by the [Communication and Network Systems Group @ University of Bonn](https://net.cs.uni-bonn.de/start-page/) and [Fraunhofer FKIE](https://www.fkie.fraunhofer.de/). The goal of our project is to create a flexible and reusable platform for malware analysis which empowers collaboration between malware researchers.

The **MASS server** contains a database of all submitted malware samples and all the gathered analysis data. **Analysis systems** are connected to the MASS server and automatically receive new samples in order to execute an analysis. Researchers can obtain the analysis results via the MASS web interface or the **REST API**.

MASS is **free and open source software** licensed under the terms of the MIT license. Other researchers are invited to contribute to the MASS development!

## Prerequisites

* **Python 3**: MASS is developed for Python 3. It *may* also run with Python 2, but we do not test this and we will not fix any bug which only arises in a Python 2 setup. In the following guide we assume that Python 3 is your system default. If it is not, please adjust the given commands according to your setup.
* **MongoDB**: MASS uses MongoDB to store samples, reports and all metadata. Please install the latest available version of MongoDB from the package repository of your distribution. We develop and test MASS with the most recent stable release of MongoDB. Thus if you run into any trouble, make sure that your MongoDB is up to date and update if necessary.
* **Python development headers and build environment**: In order to build and install necessary Python dependencies, you may need some extra software. On a Debian/Ubuntu system this is usually achieved by `apt-get install python-dev build-essential`. On a Red Hat/Fedora system, try `yum install gcc python-devel`. Please refer to the documentation of your distribution for additional details.
* **ssdeep**: MASS uses ssdeep to create fuzzy hashes of file samples. To install the Python ssdeep wrapper, you may need some extra software. Please refer to the [python-ssdeep documentation](http://python-ssdeep.readthedocs.io/en/latest/) for additional details.

## Installation

1. `git clone git@github.com:mass-project/mass_server.git && cd mass_server`
2. Install Python dependencies using a) `./make_venv.sh` to build a virtual environment, or b) `pip install -r requirements.txt` to install the necessarry packages directly to your Python 3 installation. If any error is reported, make sure you have followed the **Prerequisites** section closely.

## Startup in development mode

1. Change to the MASS server directory
2. If you have created a virtual enviroment, run `source venv_mass/bin/activate` to activate it.
3. Run `python mass_server_flask.py` to start up the MASS server in development mode. If any error is reported, make sure you have followed the **Prerequisites** section closely.

## Documentation

Coming soon!

## License

MASS is licensed under the terms of the MIT license. For additional details, please take a look at the `LICENSE` file.
