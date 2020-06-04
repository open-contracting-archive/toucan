import json
import os
import warnings
import tempfile

import flattentool
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from libcoveocds.config import LibCoveOCDSConfig
from ocdskit.util import is_package, is_record_package, is_release, is_release_package

from default.data_file import DataFile
from ocdstoucan.settings import OCDS_TOUCAN_MAXFILESIZE, OCDS_TOUCAN_MAXNUMFILES

from io import StringIO

import csv

import jsonref

from ocdskit.mapping_sheet import mapping_sheet as mapping_sheet_method

def ocds_command(request, command):
    context = {
        'maxNumOfFiles': OCDS_TOUCAN_MAXNUMFILES,
        'maxFileSize': OCDS_TOUCAN_MAXFILESIZE,
        'performAction': '/{}/go/'.format(command)
    }
    return render(request, 'default/{}.html'.format(command), context)


def get_files_from_session(request):
    for fileinfo in request.session['files']:
        yield DataFile(**fileinfo)


def json_response(files, warnings=None):
    file = DataFile('result', '.zip')
    file.write_json_to_zip(files)

    response = {
        'url': file.url,
        'size': file.size,
    }

    if warnings:
        response['warnings'] = warnings

    return JsonResponse(response)


def make_package(request, published_date, method, warnings):
    items = []
    for file in get_files_from_session(request):
        item = file.json()
        if isinstance(item, list):
            items.extend(item)
        else:
            items.append(item)

    return json_response({
        'result.json': method(items, published_date=published_date),
    }, warnings=warnings)


def invalid_request_file_message(f, file_type):
    try:
        # Don't validate XLSX or ZIP files.
        if file_type == 'xlsx zip':
            return

        data = json.load(f)

        if file_type == 'record-package':
            if not is_record_package(data):
                return _('Not a record package')
        elif file_type == 'release-package':
            if not is_release_package(data):
                return _('Not a release package')
        elif file_type == 'package release':
            if not is_release(data) and not is_package(data):
                return _('Not a release or package')
        elif file_type == 'package package-array':
            if (isinstance(data, list) and any(not is_package(item) for item in data) or
                    not isinstance(data, list) and not is_package(data)):
                return _('Not a package or list of packages')
        elif file_type == 'release release-array':
            if (isinstance(data, list) and any(not is_release(item) for item in data) or
                    not isinstance(data, list) and not is_release(data)):
                return _('Not a release or list of releases')
        else:
            return _('"%(type)s" not recognized') % {'type': file_type}
    except json.JSONDecodeError:
        return _('Error decoding JSON')

def get_options(option='https://standard.open-contracting.org/1.1/en/release-schema.json',tupleFlag=True):
    io = StringIO(newline='')
    schema = jsonref.load_uri(option)
    mapping_sheet_method(schema, io, infer_required=True)
    pathList=[]
    optionList = []

    csvList = io.getvalue().split('\n')

    for row in csvList :
        element = row.split(',')
        if len(element) > 1:
            pathList.append(element[1])

    pathList = list(set(pathList))
    del(pathList[0])
    pathList.sort()

    for element in pathList:
        optionList.append((element,element))

    if tupleFlag == True:
        return tuple(optionList)
    return pathList

def flatten(input_file, output_dir, options):

    _options = dict(options)
    preserve_fields_tmp_file = None

    if 'preserve_fields' in options:
        preserve_fields_tmp_file = tempfile.NamedTemporaryFile(delete=False)
        _options['preserve_fields'] = preserve_fields_tmp_file.name
        auxStr = ''
        for item in options['preserve_fields'] :
            auxStr = auxStr + (item + '\n')
        preserve_fields_tmp_file.write(str.encode(auxStr))
        #preserve_fields_tmp_file.write(str.encode(options['preserve_fields']))
        # it is not strictly necessary to close the file here, but doing so should make the code compatible with
        # non-Unix systems
        preserve_fields_tmp_file.close()

    config = LibCoveOCDSConfig().config

    output_name = output_dir.path + '.xlsx' if options['output_format'] == 'xlsx' else output_dir.path

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')  # flattentool uses UserWarning, so we can't set a specific category

        flattentool.flatten(
            input_file.path,
            output_name=output_name,
            main_sheet_name=config['root_list_path'],
            root_list_path=config['root_list_path'],
            root_id=config['root_id'],
            disable_local_refs=config['flatten_tool']['disable_local_refs'],
            root_is_list=False,
            **_options
        )
    if 'preserve_fields' in options:
        preserve_fields_tmp_file.close()
        os.remove(preserve_fields_tmp_file.name)
