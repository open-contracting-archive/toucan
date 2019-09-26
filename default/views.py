import io
import logging
import os
from collections import OrderedDict
from zipfile import ZipFile, ZIP_DEFLATED

import requests
import jsonref
from dateutil import parser
from django.conf import settings as django_settings
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from ocdskit.combine import package_releases as package_releases_method, compile_release_packages
from ocdskit.mapping_sheet import mapping_sheet as mapping_sheet_method
from ocdskit.upgrade import upgrade_10_11
from ocdskit.util import json_dumps, json_loads

from .decorators import require_files
from .file import FilenameHandler, save_file
from .flatten import flatten
from .forms import MappingSheetOptionsForm
from .sessions import get_files_contents, save_in_session

logger = logging.getLogger(__name__)


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
    path = name_handler.get_full_path()

    if filename is not None:
        return FileResponse(open(path, 'rb'), filename=filename, as_attachment=True)


def upgrade(request):
    """ Returns the upgrade page. """
    request.session['files'] = []
    options = django_settings.OCDS_TOUCAN_UPLOAD_OPTIONS
    options['performAction'] = '/upgrade/go/'
    return render(request, 'default/upgrade.html', options)


@require_files
def perform_upgrade(request):
    """ Performs the upgrade operation. """
    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        for filename_handler, content in get_files_contents(request.session):
            package = json_loads(content)
            package = upgrade_10_11(package)
            rezip.writestr(filename_handler.name_only_with_suffix('_updated'), json_dumps(package))
    zip_size = os.path.getsize(full_path)
    return JsonResponse({
        'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.get_id()),
        'size': zip_size,
    })


def package_releases(request):
    """ Returns the Create Release Packages page. """
    request.session['files'] = []
    options = django_settings.OCDS_TOUCAN_UPLOAD_OPTIONS
    options['performAction'] = '/package-releases/go/'
    return render(request, 'default/release-packages.html', options)


@require_files
def perform_package_releases(request):
    """ Performs the package-releases operation """
    releases = []
    kwargs = {}
    argPublishedDate = request.GET.get('publishedDate', '')
    if argPublishedDate:
        try:
            parser.parse(argPublishedDate)
            kwargs['published_date'] = argPublishedDate
        except ValueError:
            # invalid date has been received
            # TODO send a warning to client side
            logger.debug('Invalid date submitted: {}, ignoring'.format(argPublishedDate))
    for filename_handler, release in get_files_contents(request.session):
        releases.append(release)
    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        rezip.writestr('result.json', json_dumps(package_releases_method(releases, **kwargs)))
    zip_size = os.path.getsize(full_path)
    return JsonResponse({
        'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.get_id()),
        'size': zip_size,
    })


def compile(request):
    """ Compiles Releases into Records, including compiled releases by default."""
    request.session['files'] = []
    options = django_settings.OCDS_TOUCAN_UPLOAD_OPTIONS
    options['performAction'] = '/compile/go/'
    return render(request, 'default/compile.html', options)


@require_files
def perform_compile(request):
    """ Performs the compile operation. """
    packages = []
    kwargs = {'return_package': True}
    if request.GET.get('includeVersioned', '') == 'true':
        kwargs['return_versioned_release'] = True
    argPublishedDate = request.GET.get('publishedDate', '')
    if argPublishedDate:
        try:
            parser.parse(argPublishedDate)
            kwargs['published_date'] = argPublishedDate
        except ValueError:
            # invalid date has been received
            # TODO send a warning to client side
            logger.debug('Invalid date submitted: {}, ignoring'.format(argPublishedDate))
    for filename_handler, package in get_files_contents(request.session):
        packages.append(json_loads(package))
    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        rezip.writestr('result.json', json_dumps(next(compile_release_packages(packages, **kwargs))) + '\n')
    zip_size = os.path.getsize(full_path)
    return JsonResponse({
        'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.get_id()),
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
    try:
        file_conf = request.session['files'][0]
        filename_handler = FilenameHandler(**file_conf)
        flatten(filename_handler)
        url_base = '/result/{}/{}/'.format(file_conf['folder'], file_conf['id'])
        csv_size = os.path.getsize(
            os.path.join(
                filename_handler.get_folder(),
                'flatten-csv-' + file_conf['id'] + '.zip'
            )
        )
        xlsx_size = os.path.getsize(
            os.path.join(
                filename_handler.get_folder(),
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
    except Exception:
        return JsonResponse({'error': True}, status=400)


@require_POST
def uploadfile(request):
    r = {'files': []}
    upload = request.FILES['file']
    new_file_dict = save_file(upload)
    save_in_session(request.session, new_file_dict)
    r['files'].append({
        'name': upload.name,
        'size': upload.size
    })
    return JsonResponse(r)
