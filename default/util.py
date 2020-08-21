import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from ocdskit.util import is_package, is_record_package, is_release, is_release_package
from ocdsmerge.util import get_tags

from default.data_file import DataFile
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
