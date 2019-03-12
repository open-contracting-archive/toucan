import os
import io
import json
import logging
import datetime
import requests
from collections import OrderedDict
from zipfile import ZipFile, ZIP_DEFLATED
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from ocdskit.upgrade import upgrade_10_11
from .file import FilenameHandler, save_file
from .sessions import get_files_contents, save_in_session
from .ocdskit_overrides import command_package_releases, command_compile, command_mapping_sheet
from .decorators import require_files
from .forms import MappingSheetOptionsForm

# Create your views here.

UPLOAD_OPTIONS = {
    'maxNumOfFiles': 20,
    'maxFileSize': 10000000
     }

OCDS_SCHEMA_URL = 'http://standard.open-contracting.org/latest/en/release-schema.json'

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'default/index.html')

def retrieve_result(request, folder, id):
    """ Retrieve a previously generated result. """
    name_handler = FilenameHandler('result', '.zip', id=str(id), folder=folder)
    path = name_handler.get_full_path()
    return FileResponse(open(path, 'rb'), filename='result.zip', as_attachment=True)

def upgrade(request):
    """ Returns the upgrade page. """
    request.session['files'] = []
    options = UPLOAD_OPTIONS
    options['performAction'] = '/upgrade/go/'
    return render(request, 'default/upgrade.html', options)

@require_files
def perform_upgrade(request):
    """ Performs the upgrade operation. """
    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        for filename_handler, content in get_files_contents(request.session):
            package = json.loads(content, object_pairs_hook=OrderedDict)
            upgrade_10_11(package)
            rezip.writestr(filename_handler.name_only_with_suffix('_updated'), json.dumps(package))
    zip_size = os.path.getsize(full_path)
    return JsonResponse({'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.get_id()), 'size': zip_size})

def package_releases(request):
    """ Returns the Create Release Packages page. """
    request.session['files'] = []
    options = UPLOAD_OPTIONS
    options['performAction'] = '/package-releases/go/'
    return render(request, 'default/release-packages.html', UPLOAD_OPTIONS)

@require_files
def perform_package_releases(request):
    """ Performs the package-releases operation """
    releases = []
    for filename_handler, release in get_files_contents(request.session):
        releases.append(release)
    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        rezip.writestr('result.json', command_package_releases(releases))
    zip_size = os.path.getsize(full_path)
    return JsonResponse({'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.get_id()), 'size': zip_size})

def merge(request):
    """ Merges Release packages into Record Packages, including compiled releases by default."""
    request.session['files'] = []
    options = UPLOAD_OPTIONS
    options['performAction'] = '/merge/go/'
    return render(request, 'default/merge.html', UPLOAD_OPTIONS)

@require_files
def perform_merge(request):
    """ Performs the merge operation. """
    packages = []
    include_versioned = request.GET.get('includeVersioned', '') == 'true'
    for filename_handler, package in get_files_contents(request.session):
        packages.append(package)
    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w', compression=ZIP_DEFLATED) as rezip:
        rezip.writestr('result.json', command_compile(packages, include_versioned))
    zip_size = os.path.getsize(full_path)
    return JsonResponse({'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.get_id()), 'size': zip_size})

def mapping_sheet(request):
    if request.method == 'POST':
        form = MappingSheetOptionsForm(request.POST, request.FILES)
        if form.is_valid():
            logging.warning(request.FILES)
            if 'file' in request.FILES:
                # use this file
                logging.warning('Loading from file')
                json_schema = request.FILES['file'].read().decode('utf-8')
            else:
                if form.cleaned_data['url']:
                    url = form.cleaned_data['url']
                else:
                    url = OCDS_SCHEMA_URL
                json_schema = requests.get(url).text
            with io.StringIO(json_schema) as buf:
                response_content = command_mapping_sheet(buf)
            response =  HttpResponse(response_content, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="mapping-sheet.csv"'
            return response
    else:
        form = MappingSheetOptionsForm()
    return render(request, 'default/mapping_sheet.html', {'form': form}) 

@require_GET
def get_mapping_sheet(request):
    s = io.StringIO(command_mapping_sheet())
    response =  HttpResponse(s, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mapping-sheet.csv"'
    return response

@require_POST
def uploadfile(request):
    r = {'files': []}
    upload = request.FILES['file']
    new_file_dict = save_file(upload)
    save_in_session(request.session, new_file_dict)
    logger.warning(request.session['files'])
    r['files'].append({
        'name': upload.name,
        'size': upload.size
    })
    return JsonResponse(r)
