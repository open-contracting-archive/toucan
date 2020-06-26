from io import StringIO

import jsonref
from django.http import FileResponse, HttpResponse
from ocdsextensionregistry import ProfileBuilder
from ocdskit.mapping_sheet import mapping_sheet as mapping_sheet_method

from default.data_file import DataFile


def get_mapping_sheet_from_url(url, as_response=False):
    schema = jsonref.load_uri(url)
    return _get_mapping_sheet(schema, as_response)


def get_mapping_sheet_from_uploaded_file(uploaded):
    schema = jsonref.load(uploaded)
    return _get_mapping_sheet(schema)


def get_extended_mapping_sheet(extensions, version, as_response=False):
    builder = ProfileBuilder(version, extensions)
    schema = jsonref.JsonRef.replace_refs(builder.patched_release_schema())
    return _get_mapping_sheet(schema, as_response)


def _get_mapping_sheet(data, as_response=False):
    io = StringIO()
    mapping_sheet_method(data, io, infer_required=True)

    if as_response:
        response = HttpResponse(io.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="result.csv"'
        return response

    data_file = DataFile('result', '.csv')
    data_file.write(io.getvalue().encode('utf-8'))

    return {
        'url': data_file.url + 'csv/',
        'driveUrl': data_file.url.replace('result', 'google-drive-save-start') + 'csv/',
        'size': data_file.size
    }
