import json
import os
import shutil
import warnings
from collections import OrderedDict
from urllib.parse import urlparse
from zipfile import ZIP_DEFLATED, ZipFile

import flattentool
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST
from jsonref import requests
from libcoveocds.config import LibCoveOCDSConfig
from ocdskit.combine import combine_record_packages, combine_release_packages, merge
from ocdskit.combine import package_releases as package_releases_method
from ocdskit.upgrade import upgrade_10_11
from requests.exceptions import ConnectionError, HTTPError, SSLError

from default.data_file import DataFile
from default.decorators import clear_files, published_date, require_files, validate_optional_args, validate_split_size
from default.forms import MappingSheetOptionsForm
from default.mapping_sheet import (get_extended_mapping_sheet, get_mapping_sheet_from_uploaded_file,
                                   get_mapping_sheet_from_url)
from default.util import (get_files_from_session, invalid_request_file_message, json_response, make_package,
                          ocds_command)


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
    return render(request, 'default/to-spreadsheet.html')


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
def split_packages(request):
    return ocds_command(request, 'split-packages')


@clear_files
def upgrade(request):
    return ocds_command(request, 'upgrade')


@require_files
@validate_optional_args
def perform_upgrade(request, pretty_json=False, encoding='utf-8', warnings=None):
    data = {}
    for file in get_files_from_session(request):
        data.update({file.name_with_suffix('upgraded'): upgrade_10_11(
            file.json(codec=encoding, object_pairs_hook=OrderedDict))})
    return json_response(data, warnings, pretty_json, encoding)


@require_files
@published_date
@validate_optional_args
def perform_package_releases(request, pretty_json=False, published_date='', encoding='utf-8', warnings=None):
    method = package_releases_method
    return make_package(request, published_date, method, pretty_json, encoding, warnings)


@require_files
@published_date
@validate_optional_args
def perform_combine_packages(request, pretty_json=False, published_date='', encoding='utf-8', warnings=None):
    if request.GET.get('packageType') == 'release':
        method = combine_release_packages
    else:
        method = combine_record_packages
    return make_package(request, published_date, method, pretty_json, encoding, warnings)


@require_files
@published_date
@validate_optional_args
@validate_split_size
def perform_split_packages(request, pretty_json=False, published_date='', size=1, encoding='utf-8', warnings=None):
    change_published_date = request.GET.get('changePublishedDate') == 'true'
    packages = [file.json(codec=encoding) for file in get_files_from_session(request)]

    if request.GET.get('packageType') == 'release':
        package_data = 'releases'
    else:
        package_data = 'records'

    if not published_date:
        change_published_date = False

    count = 0
    result = {}

    for package in packages:
        if isinstance(package, list):
            packages.extend(package)
            continue

        context = package[package_data]

        # based on:
        # cdskit/ocdskit/cli/commands/split_record_packages.py
        # cdskit/ocdskit/cli/commands/split_release_packages.py

        # we don't know which packages were used for each record.
        if package_data == 'records' and 'packages' in package:
            del package['packages']

        for i in range(0, len(context), size):
            count += 1
            name = "result{}.json".format(count)
            content = dict(package)
            if change_published_date:
                content['publishedDate'] = published_date
            content[package_data] = context[i:i + size]
            result.update({name: content})

    return json_response(result, warnings, pretty_json, encoding)


@require_files
@published_date
@validate_optional_args
def perform_compile(request, pretty_json=False, published_date='', encoding='utf-8', warnings=None):
    packages = [file.json(codec=encoding) for file in get_files_from_session(request)]
    return_versioned_release = request.GET.get('includeVersioned') == 'true'

    return json_response({
        'result.json': next(merge(packages, return_package=True, published_date=published_date,
                                  return_versioned_release=return_versioned_release)),
    }, warnings, pretty_json, encoding)


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
    input_file = next(get_files_from_session(request))
    output_dir = DataFile('flatten', '', input_file.id, input_file.folder)

    config = LibCoveOCDSConfig().config
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')  # flattentool uses UserWarning, so we can't set a specific category

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

    # Create a ZIP file of the CSV files, and delete the output CSV files.
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
@validate_optional_args
def perform_to_json(request, pretty_json=False, encoding='utf-8', warnings=None):
    input_file = next(get_files_from_session(request))
    output_dir = DataFile('unflatten', '', input_file.id, input_file.folder)

    output_name = output_dir.path + '.json'
    extension = os.path.splitext(input_file.path)[1]
    if extension == '.xlsx':
        input_file_path = input_file.path
        input_format = 'xlsx'
    else:
        input_file_path = output_dir.path
        input_format = 'csv'
        if extension == '.zip':
            with ZipFile(input_file.path) as zipfile:
                for name in zipfile.namelist():
                    zipfile.extract(name, input_file_path)
        else:
            if extension == '.csv':
                os.mkdir(input_file_path)
                shutil.copy(input_file.path, input_file_path)

    config = LibCoveOCDSConfig().config
    flattentool.unflatten(
        input_file_path,
        input_format=input_format,
        output_name=output_name,
        root_list_path=config['root_list_path'],
        root_id=config['root_id']
    )

    # Delete the input CSV files, if any.
    if extension in ('.csv', '.zip'):
        shutil.rmtree(input_file_path)

    with open(output_name) as json_file:
        return json_response({'result.json': json.load(json_file)}, warnings, pretty_json, encoding)


@require_POST
def upload_url(request):
    request.session['files'] = []
    errors = []
    status = 401

    for data in request.POST:
        if 'input_url' in data:
            url = request.POST.get(data)
            basename = data
            if request.POST.get('type') == 'csv xlsx zip':
                extension = os.path.splitext(urlparse(url).path)[1]
            else:
                extension = ".json"
            folder = 'media'
            data_file = DataFile(basename, extension)

            try:
                os.stat(folder + '/' + data_file.folder)
            except FileNotFoundError:
                os.mkdir(folder + '/' + data_file.folder)

            try:
                urlparse(url)
                with requests.get(url, stream=True) as request_file:
                    request_file.raise_for_status()
                    with open(data_file.path, 'wb+') as f:
                        for chunk in request_file.iter_content(chunk_size=8*1024):
                            if chunk:
                                f.write(chunk)

            except ValueError:
                status = 400
                errors.append({'id': data, 'message': _('Enter a valid URL.')})

            except (HTTPError, ConnectionError, SSLError):
                status = 400
                message = _('There was an error when trying to access this URL. '
                            'Please verify that the URL is correct and the file has the expected format.')
                errors.append({'id': data, 'message': message})

            else:
                with open(data_file.path, 'rb') as f:
                    file_type = request.POST.get('type', None)
                    message = invalid_request_file_message(f, file_type)
                    if message:
                        errors.append({'id': data, 'message': message})
                    else:
                        request.session['files'].append(data_file.as_dict())
                        request.session.modified = True
                        request.session.save()

    if len(errors) > 0:
        return JsonResponse(errors, status=status, safe=False)

    return JsonResponse({
        'files': request.session['files']
    })


@require_GET
def upload_url_status(request):
    return JsonResponse(len(request.session['files']), safe=False)


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
