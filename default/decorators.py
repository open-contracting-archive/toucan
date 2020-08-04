import os
from functools import wraps
from zipfile import ZipFile

from dateutil import parser
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _

from default.data_file import DataFile
from default.util import invalid_request_file_message


def clear_files(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        request.session['files'] = []
        return function(request, *args, **kwargs)

    return wrap


def validate_files(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if 'files' not in request.session:
            return JsonResponse({'error': 'No files uploaded'}, status=400, reason='No files available for operation')

        send_result = request.GET.get('sendResult')
        if send_result:
            # Set files session to the last generated results
            for file in request.session['results']:
                data_file = DataFile(**file)
                # All json results are compressed in a zip file
                if data_file.ext == '.zip':
                    with ZipFile(data_file.path) as zipfile:
                        for f in zipfile.infolist():
                            prefix, ext = os.path.splitext(f.filename)
                            new_file = DataFile(prefix, ext)
                            path, f.filename = os.path.split(new_file.path)
                            zipfile.extract(f, 'media/' + new_file.folder)
                            # Open the file to check if it is the correct type
                            with open(new_file.path, 'rb') as h:
                                file_type = request.GET.get('type', None)
                                message = invalid_request_file_message(h, file_type)
                                if message:
                                    return HttpResponse(message, status=401)  # error 401 for invalid type
                                else:
                                    request.session['files'].append(new_file.as_dict())
            request.session.modified = True

        return function(request, *args, **kwargs)

    return wrap


def published_date(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        published_date = request.GET.get('publishedDate', '')
        if published_date:
            try:
                parser.parse(published_date)
            except ValueError:
                kwargs['warnings'] = [
                    _('An invalid published date was submitted, and therefore ignored: %(date)s') % {
                        'date': published_date,
                    },
                ]
            else:
                kwargs['published_date'] = published_date
        return function(request, *args, **kwargs)

    return wrap
