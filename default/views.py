import os
import shutil
from collections import OrderedDict
from zipfile import ZIP_DEFLATED, ZipFile

import flattentool
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST
from libcoveocds.config import LibCoveOCDSConfig
from ocdskit.combine import combine_record_packages, combine_release_packages, merge
from ocdskit.combine import package_releases as package_releases_method
from ocdskit.upgrade import upgrade_10_11

from default.data_file import DataFile
from default.decorators import clear_files, published_date, require_files
from default.forms import MappingSheetOptionsForm, UnflattenOptionsForm
from default.mapping_sheet import (get_extended_mapping_sheet, get_mapping_sheet_from_uploaded_file,
                                   get_mapping_sheet_from_url)
from default.util import (get_files_from_session, get_options, invalid_request_file_message, json_response, make_package,
                          ocds_command, flatten)

from django.views.decorators.csrf import csrf_exempt


def retrieve_result(request, folder, id, format=None):
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

    file = DataFile(prefix, ext, id=str(id), folder=folder)
    return FileResponse(open(file.path, 'rb'), filename=filename, as_attachment=True)


def index(request):
    return render(request, 'default/index.html')


@clear_files
def to_spreadsheet(request):
    return render(request, 'default/to-spreadsheet.html', {'form': UnflattenOptionsForm()})


@clear_files
def to_json(request):
    return render(request, 'default/to-json.html')


@clear_files
def compile(request):
    return ocds_command(request, 'compile')


@clear_files
def package_releases(request):
    return ocds_command(request, 'package-releases')


@clear_files
def combine_packages(request):
    return ocds_command(request, 'combine-packages')


@clear_files
def upgrade(request):
    return ocds_command(request, 'upgrade')


@require_files
def perform_upgrade(request):
    return json_response((file.name_with_suffix('upgraded'), upgrade_10_11(file.json(object_pairs_hook=OrderedDict)))
                         for file in get_files_from_session(request))

@csrf_exempt
@require_GET
def get_option_list(request):
    options1 = get_options('https://standard.open-contracting.org/1.1/en/release-schema.json', tupleFlag=False)
    options2 = get_options('http://standard.open-contracting.org/1.1/es/release-schema.json', tupleFlag=False)
    options3 = get_options('https://standard.open-contracting.org/schema/1__0__3/release-schema.json', tupleFlag=False)
    return JsonResponse({
                        'options1' : options1,
                        'options2' : options2,
                        'options3' : options3
                        })

@require_files
@published_date
def perform_package_releases(request, published_date='', warnings=None):
    method = package_releases_method
    return make_package(request, published_date, method, warnings)


@require_files
@published_date
def perform_combine_packages(request, published_date='', warnings=None):
    if request.GET.get('packageType') == 'release':
        method = combine_release_packages
    else:
        method = combine_record_packages
    return make_package(request, published_date, method, warnings)


@require_files
@published_date
def perform_compile(request, published_date='', warnings=None):
    packages = [file.json() for file in get_files_from_session(request)]
    return_versioned_release = request.GET.get('includeVersioned') == 'true'

    return json_response({
        'result.json': next(merge(packages, return_package=True, published_date=published_date,
                                  return_versioned_release=return_versioned_release)),
    }, warnings)


def mapping_sheet(request):
    if request.method == 'POST':
        form = MappingSheetOptionsForm(request.POST, request.FILES)

        if form.is_valid():
            type_selected = form.cleaned_data['type']
            if type_selected == 'select':
                return get_mapping_sheet_from_url(form.cleaned_data['select_url'])
            if type_selected == 'url':
                return get_mapping_sheet_from_url(form.cleaned_data['custom_url'])
            if type_selected == 'file':
                return get_mapping_sheet_from_uploaded_file(request.FILES['custom_file'])
            if type_selected == 'extension':
                return get_extended_mapping_sheet(form.cleaned_data['extension_urls'], form.cleaned_data['version'])

    elif request.method == 'GET':
        if 'source' in request.GET:
            return get_mapping_sheet_from_url(request.GET['source'])
        if 'extension' in request.GET:
            if 'version' in request.GET:
                version = request.GET['version']
            else:
                version = '1__1__4'
            return get_extended_mapping_sheet(request.GET.getlist('extension'), version)

        form = MappingSheetOptionsForm()

    context = {
        'form': form
    }

    return render(request, 'default/mapping_sheet.html', context)


@require_files
@require_POST
def perform_to_spreadsheet(request):
    input_file = next(get_files_from_session(request))
    output_dir = DataFile('flatten', '', input_file.id, input_file.folder)

    form = UnflattenOptionsForm(request.POST,request.POST.__getitem__('schema')[0])

    if not form.is_valid():
        return JsonResponse({'form_errors': dict(form.errors)}, status=400)

    flatten(input_file, output_dir, form.non_empty_values())

    response = {}
    if form.cleaned_data['output_format'] == 'all' or form.cleaned_data['output_format'] == 'csv':
        # Create a ZIP file of the CSV files, and delete the output CSV files.
        csv_zip = DataFile('flatten-csv', '.zip', id=input_file.id, folder=input_file.folder)
        with ZipFile(csv_zip.path, 'w', compression=ZIP_DEFLATED) as zipfile:
            for filename in os.listdir(output_dir.path):
                zipfile.write(os.path.join(output_dir.path, filename), filename)
        shutil.rmtree(output_dir.path)

        response['csv'] = {
            'url': input_file.url + 'csv/',
            'size': csv_zip.size,
        }

    if form.cleaned_data['output_format'] == 'all' or form.cleaned_data['output_format'] == 'xlsx':
        response['xlsx'] = {
            'url': input_file.url + 'xlsx/',
            'size': os.path.getsize(output_dir.path + '.xlsx'),
        }

    return JsonResponse(response)


@require_files
def perform_to_json(request):
    input_file = next(get_files_from_session(request))
    output_dir = DataFile('unflatten', '', input_file.id, input_file.folder)

    output_name = output_dir.path + '.json'
    extension = os.path.splitext(input_file.path)[1]
    if extension == '.zip':
        input_file_path = output_dir.path + '/tmp'
        input_format = 'csv'
        with ZipFile(input_file.path) as zipfile:
            for name in zipfile.namelist():
                zipfile.extract(name, input_file_path)
    else:
        input_file_path = input_file.path
        input_format = 'xlsx'

    config = LibCoveOCDSConfig().config
    flattentool.unflatten(
        input_file_path,
        input_format=input_format,
        output_name=output_name,
        root_list_path=config['root_list_path'],
        root_id=config['root_id']
    )

    # Delete the input CSV files, if any.
    if extension == '.zip':
        shutil.rmtree(input_file_path)

    # Create a ZIP file of the JSON file.
    json_zip = DataFile('result', '.zip', id=input_file.id, folder=input_file.folder)
    with ZipFile(json_zip.path, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.write(output_name, 'result.json')

    return JsonResponse({
        'url': input_file.url,
        'size': json_zip.size,
    })


@require_POST
def uploadfile(request):
    request_file = request.FILES['file']
    basename, extension = os.path.splitext(request_file.name)

    data_file = DataFile(basename, extension)
    file_type = request.POST.get('type', None)

    message = invalid_request_file_message(request_file, file_type)
    if message:
        return HttpResponse(message, status=400)
    else:
        data_file.write(request_file)

    if 'files' not in request.session:
        request.session['files'] = []
    request.session['files'].append(data_file.as_dict())
    # https://docs.djangoproject.com/en/2.2/topics/http/sessions/#when-sessions-are-saved
    request.session.modified = True

    return JsonResponse({
        'files': [{
            'id': data_file.id,
            'name': request_file.name,
            'size': request_file.size,
        }],
    })


@require_GET
def deletefile(request, id):
    if 'files' not in request.session:
        return JsonResponse({'message': _('File not found')}, status=404)

    for fileinfo in request.session['files']:
        if fileinfo['id'] == str(id):
            request.session['files'].remove(fileinfo)
            request.session.modified = True
            return JsonResponse({'message': _('File deleted')})

    return JsonResponse({'message': _('File not found')}, status=404)
