import json
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from ocdskit.util import is_record_package, is_release_package, json_loads

from default.data_file import DataFile
from ocdstoucan.settings import OCDS_TOUCAN_MAXFILESIZE, OCDS_TOUCAN_MAXNUMFILES

logger = logging.getLogger(__name__)


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


def file_is_valid(file, ocds_type=None):
    try:
        data = json_loads(file.read())
        if ocds_type == 'release-package':
            if not is_release_package(data):
                return False, _('Not a release package')
        elif ocds_type == 'record-package':
            if not is_record_package(data):
                return False, _('Not a record package')
        return True, ''
    except json.JSONDecodeError:
        logger.debug('Error decoding file {}'.format(file.name))
        return False, _('Error decoding JSON')
