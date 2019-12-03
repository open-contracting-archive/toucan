import os
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

import flattentool
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from libcoveocds.config import LibCoveOCDSConfig
from ocdskit.combine import compile_release_packages
from ocdskit.combine import package_releases as package_releases_method
from ocdskit.upgrade import upgrade_10_11

from default.data_file import DataFile
from default.decorators import clear_files, published_date, require_files
from default.forms import MappingSheetOptionsForm
from default.mapping_sheet import (get_extended_mapping_sheet, get_mapping_sheet_from_uploaded_file,
                                   get_mapping_sheet_from_url)
from ocdstoucan.settings import OCDS_TOUCAN_MAXFILESIZE, OCDS_TOUCAN_MAXNUMFILES


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
    elif format == 'json':
        prefix = 'unflatten'
        ext = '.json'
        filename = 'result.json'
    else:
        raise Http404('Invalid option')

    file = DataFile(prefix, ext, id=str(id), folder=folder)
    return FileResponse(open(file.path, 'rb'), filename=filename, as_attachment=True)


def _ocds_command(request, command):
    context = {
        'maxNumOfFiles': OCDS_TOUCAN_MAXNUMFILES,
        'maxFileSize': OCDS_TOUCAN_MAXFILESIZE,
        'performAction': '/{}/go/'.format(command)
    }
    return render(request, 'default/{}.html'.format(command), context)


def index(request):
    return render(request, 'default/index.html')


@clear_files
def to_spreadsheet(request):
    return render(request, 'default/to-spreadsheet.html')


@clear_files
def to_json(request):
    return render(request, 'default/to-json.html')


@clear_files
def compile(request):
    return _ocds_command(request, 'compile')


@clear_files
def package_releases(request):
    return _ocds_command(request, 'package-releases')


@clear_files
def upgrade(request):
    return _ocds_command(request, 'upgrade')


def _get_files_from_session(request):
    for fileinfo in request.session['files']:
        yield DataFile(**fileinfo)


def _json_response(files):
    file = DataFile('result', '.zip')
    file.write_json_to_zip(files)

    return JsonResponse({
        'url': file.url,
        'size': file.size,
    })


@require_files
def perform_upgrade(request):
    return _json_response((file.name_with_suffix('upgraded'), upgrade_10_11(file.json()))
                          for file in _get_files_from_session(request))


@require_files
@published_date
def perform_package_releases(request, published_date=''):
    releases = []
    for file in _get_files_from_session(request):
        item = file.json()
        if isinstance(item, list):
            releases.extend(item)
        else:
            releases.append(item)

    return _json_response({
        'result.json': package_releases_method(releases, published_date=published_date),
    })


@require_files
@published_date
def perform_compile(request, published_date=''):
    packages = [file.json() for file in _get_files_from_session(request)]
    return_versioned_release = request.GET.get('includeVersioned') == 'true'

    return _json_response({
        'result.json': next(compile_release_packages(packages, return_package=True, published_date=published_date,
                                                     return_versioned_release=return_versioned_release)),
    })


def mapping_sheet(request):
    if request.method == 'POST':
        form = MappingSheetOptionsForm(request.POST, request.FILES)

        if form.is_valid():
            type_selected = form.cleaned_data['type']
            if type_selected == 'select':
                return get_mapping_sheet_from_url(form.cleaned_data['select_url'])
            elif type_selected == 'url':
                return get_mapping_sheet_from_url(form.cleaned_data['custom_url'])
            elif type_selected == 'file':
                return get_mapping_sheet_from_uploaded_file(request.FILES['custom_file'])
            elif type_selected == 'extension':
                return get_extended_mapping_sheet(form.cleaned_data['extension_urls'], form.cleaned_data['version'])

    elif request.method == 'GET':
        if 'source' in request.GET:
            return get_mapping_sheet_from_url(request.GET['source'])
        elif 'extension' in request.GET:
            if 'version' in request.GET:
                version = request.GET['version']
            else:
                version = '1__1__4'
            return get_extended_mapping_sheet(request.GET.getlist('extension'), version)

        form = MappingSheetOptionsForm()

    context = {
        'form': form,
        'versionOptions': {
            '1.1': {
                'Release': 'https://standard.open-contracting.org/1.1/en/release-schema.json',
                'Release Package': 'https://standard.open-contracting.org/1.1/en/release-package-schema.json',
                'Record Package': 'https://standard.open-contracting.org/1.1/en/record-package-schema.json',
            },
            '1.1 (Español)': {
                'Release': 'http://standard.open-contracting.org/1.1/es/release-schema.json',
                'Paquete de Release': 'http://standard.open-contracting.org/1.1/es/release-schema.json',
                'Paquete de Record': 'http://standard.open-contracting.org/1.1/es/record-package-schema.json',
            },
            '1.0': {
                'Release': 'https://standard.open-contracting.org/schema/1__0__3/release-schema.json',
                'Release Package': 'https://standard.open-contracting.org/schema/1__0__3/release-package-schema.json',
                'Record Package': 'https://standard.open-contracting.org/schema/1__0__3/record-package-schema.json',
            },
        },
    }

    return render(request, 'default/mapping_sheet.html', context)


@require_files
def perform_to_spreadsheet(request):
    input_file = next(_get_files_from_session(request))
    output_dir = DataFile('flatten', '', input_file.id, input_file.folder)

    config = LibCoveOCDSConfig().config
    flattentool.flatten(
        input_file.path,
        output_name=output_dir.path,
        main_sheet_name=config['root_list_path'],
        root_list_path=config['root_list_path'],
        root_id=config['root_id'],
        schema=config['schema_version_choices']['1.1'][1] + 'release-schema.json',
        disable_local_refs=config['flatten_tool']['disable_local_refs'],
        remove_empty_schema_columns=config['flatten_tool']['remove_empty_schema_columns'],
        root_is_list=False,
    )

    # Create a ZIP file of the CSV files, and delete the CSV files.
    csv_zip = DataFile('flatten-csv', '.zip', id=input_file.id, folder=input_file.folder)
    with ZipFile(csv_zip.path, 'w', compression=ZIP_DEFLATED) as zipfile:
        for filename in os.listdir(output_dir.path):
            zipfile.write(os.path.join(output_dir.path, filename), filename)
    shutil.rmtree(output_dir.path)

    return JsonResponse({
        'csv': {
            'url': input_file.url + 'csv/',
            'size': csv_zip.size,
        },
        'xlsx': {
            'url': input_file.url + 'xlsx/',
            'size': os.path.getsize(output_dir.path + '.xlsx'),
        }
    })


@require_files
def perform_to_json(request):
    input_file = next(_get_files_from_session(request))
    output_dir = DataFile('unflatten', '', input_file.id, input_file.folder)

    path_file, format_file = os.path.splitext(input_file.path)
    if format_file == '.zip':
        format_file = "csv"
        path_file = 'temp'
        with ZipFile(input_file.path, 'r') as zipfile:
            zipfile.extractall('temp')
    else:
        format_file = "xlsx"
        path_file = input_file.path

    config = LibCoveOCDSConfig().config
    flattentool.unflatten(
        path_file,
        input_format=format_file,
        output_name=output_dir.path + '.json',
        root_list_path=config['root_list_path'],
        root_id=config['root_id']
    )

    return JsonResponse({
        'url': input_file.url + 'json/',
        'size': os.path.getsize(output_dir.path + '.json'),
    })


@require_POST
def uploadfile(request):
    request_file = request.FILES['file']
    name, extension = os.path.splitext(request_file.name)

    file = DataFile(name, extension)
    file.write(request_file)

    if 'files' not in request.session:
        request.session['files'] = []
    request.session['files'].append(file.as_dict())
    # https://docs.djangoproject.com/en/2.2/topics/http/sessions/#when-sessions-are-saved
    request.session.modified = True

    return JsonResponse({
        'files': [{
            'name': request_file.name,
            'size': request_file.size,
        }],
    })
