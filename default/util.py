import base64
import copy
import hashlib
import io
import json
import os
import tempfile
import warnings

import flattentool
import jsonref
import jsonschema
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from libcoveocds.config import LibCoveOCDSConfig
from ocdskit.util import is_package, is_record_package, is_release, is_release_package
from ocdsmerge.util import get_tags

from default.data_file import DataFile
from default.mapping_sheet import mapping_sheet_method
from ocdstoucan.settings import OCDS_TOUCAN_MAXFILESIZE, OCDS_TOUCAN_MAXNUMFILES


def ocds_tags():
    return cache.get_or_set('git_tags', sorted(get_tags(), reverse=True), 3600)


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
        'driveUrl': file.url.replace('result', 'google-drive-save-start')
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
        # Only validate JSON files.
        if file_type == 'csv xlsx zip':
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


def get_schema_field_list(option):

    def make_list():
        buff = io.StringIO(newline='')
        schema = jsonref.load_uri(option)
        mapping_sheet_method(schema, buff, infer_required=True)
        path_list = []
        option_list = []

        csv_list = buff.getvalue().split('\n')

        for row in csv_list:
            element = row.split(',')
            if len(element) > 1:
                path_list.append(element[1])

        path_list = list(set(path_list))
        del(path_list[0])
        path_list.sort()

        for element in path_list:
            option_list.append((element, element))

        return tuple(option_list)

    key = get_cache_name('schema_val_options', option)
    return cache.get_or_set(key, make_list, 60*60*24*2)


def resolve_schema_refs(schema):
    # Django templates seem to have problems with the proxies used by jsonref, so the only solution seems to be a
    # custom method.
    resolver = jsonschema.RefResolver.from_schema(copy.deepcopy(schema))

    def resolve_refs(obj):
        schema_def = obj
        if '$ref' in obj:
            ref, schema_def = copy.deepcopy(resolver.resolve(obj['$ref']))
            schema_def.update(obj)
        if 'properties' in schema_def:
            for key, value in schema_def['properties'].items():
                schema_def['properties'][key] = resolve_refs(value)
        if 'items' in schema_def:
            schema_def['items'] = resolve_refs(schema_def['items'])
        return schema_def

    return resolve_refs(schema)


def flatten(input_file, output_dir, options):

    _options = dict(options)
    preserve_fields_tmp_file = None

    if 'preserve_fields' in options:
        preserve_fields_tmp_file = tempfile.NamedTemporaryFile(delete=False)
        _options['preserve_fields'] = preserve_fields_tmp_file.name
        aux_str = ''
        for item in options['preserve_fields']:
            aux_str = aux_str + (item + '\n')
        preserve_fields_tmp_file.write(str.encode(aux_str))
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


def get_cache_name(key, param):
    return key + '_' + str(base64.b64encode(hashlib.md5(param.encode('utf-8')).digest()))
