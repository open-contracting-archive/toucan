import io
import os
from collections import OrderedDict
from zipfile import ZipFile, ZIP_DEFLATED

import requests
import jsonref
from django.conf import settings as django_settings
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from ocdskit.combine import package_releases as package_releases_method, compile_release_packages
from ocdskit.mapping_sheet import mapping_sheet as mapping_sheet_method
from ocdskit.upgrade import upgrade_10_11
from ocdskit.util import json_dumps, json_loads

from .decorators import published_date, require_files
from .file import FilenameHandler
from .flatten import flatten
from .forms import MappingSheetOptionsForm
from .sessions import get_files_contents


def index(request):
    return render(request, 'default/index.html')


def retrieve_result(request, folder, id, format=None):
    """ Retrieve a previously generated result. """

    filename = None
    if format is None:
        prefix = 'result'
        ext = '.zip'
        filename = 'result.zip'
    elif format == 'csv':
        prefix = 'flatten-csv'
        ext = '.zip'
        filename = 'result-csv.zip'
    elif format == 'xlsx':
        prefix = 'flatten'
        ext = '.xlsx'
        filename = 'result.xlsx'
    else:
        raise Http404('Invalid option')

    name_handler = FilenameHandler(prefix, ext, id=str(id), folder=folder)
    path = name_handler.path

    if filename is not None:
        return FileResponse(open(path, 'rb'), filename=filename, as_attachment=True)


def _ocds_command(request, command):
    request.session['files'] = []
    options = django_settings.OCDS_TOUCAN_UPLOAD_OPTIONS
    options['performAction'] = '/{}/go/'.format(command)
    return render(request, 'default/{}.html'.format(command), options)


def compile(request):
    return _ocds_command(request, 'compile')


def package_releases(request):
    return _ocds_command(request, 'package-releases')


def upgrade(request):
    return _ocds_command(request, 'upgrade')


@require_files
def perform_upgrade(request):
    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        for filename_handler, content in get_files_contents(request.session):
            package = upgrade_10_11(json_loads(content))
            rezip.writestr(filename_handler.name_with_suffix('_updated'), json_dumps(package) + '\n')

    zip_size = os.path.getsize(full_path)
    return JsonResponse({
        'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.id),
        'size': zip_size,
    })


@require_files
@published_date
def perform_package_releases(request, published_date=''):
    releases = []
    kwargs = {
        'published_date': published_date,
    }
    for filename_handler, release in get_files_contents(request.session):
        releases.append(json_loads(release))

    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        rezip.writestr('result.json', json_dumps(package_releases_method(releases, **kwargs)) + '\n')

    zip_size = os.path.getsize(full_path)
    return JsonResponse({
        'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.id),
        'size': zip_size,
    })


@require_files
@published_date
def perform_compile(request, published_date=''):
    packages = []
    kwargs = {
        'published_date': published_date,
        'return_package': True,
    }
    if request.GET.get('includeVersioned', '') == 'true':
        kwargs['return_versioned_release'] = True
    for filename_handler, package in get_files_contents(request.session):
        packages.append(json_loads(package))

    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        rezip.writestr('result.json', json_dumps(next(compile_release_packages(packages, **kwargs))) + '\n')

    zip_size = os.path.getsize(full_path)
    return JsonResponse({
        'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.id),
        'size': zip_size,
    })


def mapping_sheet(request):
    options = django_settings.OCDS_TOUCAN_SCHEMA_OPTIONS
    dic = {
        'versionOptions': options
    }
    if request.method == 'POST':
        form = MappingSheetOptionsForm(request.POST)
        if form.is_valid():
            file_type, ocds_version = form.cleaned_data['version'].split('-', 1)
            if file_type in options and ocds_version in options[file_type]:
                json_schema = jsonref.loads(requests.get(
                    options[file_type][ocds_version]).text, object_pairs_hook=OrderedDict)
                buf = io.StringIO()
                mapping_sheet_method(json_schema, buf)
                response = HttpResponse(buf.getvalue(), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="mapping-sheet.csv"'
                return response
        dic['error'] = _('Invalid option! Please verify and try again')
    return render(request, 'default/mapping_sheet.html', dic)


def to_spreadsheet(request):
    request.session['files'] = []
    return render(request, 'default/to-spreadsheet.html')


@require_files
def perform_to_spreadsheet(request):
    res = {}
    file_conf = request.session['files'][0]
    filename_handler = FilenameHandler(**file_conf)
    flatten(filename_handler)
    url_base = '/result/{}/{}/'.format(file_conf['folder'], file_conf['id'])
    csv_size = os.path.getsize(
        os.path.join(
            filename_handler.directory,
            'flatten-csv-' + file_conf['id'] + '.zip'
        )
    )
    xlsx_size = os.path.getsize(
        os.path.join(
            filename_handler.directory,
            'flatten-' + file_conf['id'] + '.xlsx'
        )
    )
    res = {
        'csv': {
            'url': url_base + 'csv/',
            'size': csv_size
        },
        'xlsx': {
            'url': url_base + 'xlsx/',
            'size': xlsx_size
        }
    }
    return JsonResponse(res)


@require_POST
def uploadfile(request):
    file = request.FILES['file']
    name, extension = os.path.splitext(file.name)
    handler = FilenameHandler(name, extension)

    path = handler.generate_full_path()
    with open(path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    if 'files' not in request.session:
        request.session['files'] = []
    request.session['files'].append(handler.as_dict())
    request.session.modified = True

    return JsonResponse({
        'files': [{
            'name': file.name,
            'size': file.size,
        }],
    })
