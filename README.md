[Spanish](https://github.com/open-contracting/toucan/blob/master/README_es.md)

# OCDS Toucan

[![Build Status](https://travis-ci.org/open-contracting/toucan.svg)](https://travis-ci.org/open-contracting/toucan) [![Coverage Status](https://coveralls.io/repos/github/open-contracting/toucan/badge.svg?branch=master)](https://coveralls.io/github/open-contracting/toucan?branch=master)

OCDS Toucan is a web application to transform OCDS files using [OCDS Kit](https://github.com/open-contracting/ocdskit), and to convert OCDS files to CSV or Excel using [Flatten Tool](https://github.com/OpenDataServices/flatten-tool).

## Installation
### Requirements
1. Python 3.6+ or higher

### Installation
Clone the repository and change to the new directory:

```sh
git clone git@github.com:open-contracting/toucan.git
cd toucan
```

Create a virtual environment:

```sh
virtualenv -p python3 .ve
```

Activate the virtual environment:

```sh
source .ve/bin/activate
```

Install the requirements:

```sh
pip install -r requirements.txt
```

### Configuration
Set the following environment variables:
* OCDS_TOUCAN_MEDIA_ROOT: path of the directory where the uploaded files will be stored. By default is the `media` folder inside the project's directory.
* OCDS_TOUCAN_LOCALE_PATH: lookup path for .PO files. By default is the `locale` folder inside the project's directory.
* OCDS_TOUCAN_MAXNUMFILES: max number of files to upload per request. Default value is 20.
* OCDS_TOUCAN_MAXFILESIZE: max size of files to upload in bytes. Default value is 10MB.

### Deployment

To start the development server run:

```sh
python manage.py runserver
```