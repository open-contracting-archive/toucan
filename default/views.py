import os
import json
import logging
import datetime
from collections import OrderedDict
from zipfile import ZipFile
from django.http import JsonResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .file import FilenameHandler, save_file
from .sessions import get_files, has_files, save_in_session
from ocdskit.upgrade import upgrade_10_11

# Create your views here.

UPLOAD_OPTIONS = {
    'maxNumOfFiles': 20,
    'maxFileSize': 10000000
     }

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
    return render(request, 'default/upgrade.html', UPLOAD_OPTIONS)

def perform_upgrade(request):
    """ Performs the upgrade operation. """
    if not has_files(request.session):
        return JsonResponse({'error': 'No files uploaded'})
    zipname_handler = FilenameHandler('result', '.zip')
    full_path = zipname_handler.generate_full_path()
    with ZipFile(full_path, 'w') as rezip:
        logger.warning('hola')
        logger.warning(len(request.session['files']))
        for file_dict, size in get_files(request.session):
            file_handler = FilenameHandler(**file_dict)
            filename = file_handler.get_full_path()
            with open(filename, 'r', encoding='utf-8') as f:
                package = json.load(f,object_pairs_hook=OrderedDict)
                upgrade_10_11(package)
                rezip.writestr(file_handler.name_only_with_suffix('_updated'), json.dumps(package))
    zip_size = os.path.getsize(full_path)
    return JsonResponse({'url': '/result/{}/{}/'.format(zipname_handler.folder, zipname_handler.get_id()), 'size': zip_size}) 

@require_POST
def uploadfile(request):
    r = {'files': []}
    upload = request.FILES['file']
    new_file_dict = save_file(upload)
    save_in_session(request.session, new_file_dict, upload.size)
    r['files'].append({
        'name': upload.name,
        'size': upload.size
    })
    return JsonResponse(r)
