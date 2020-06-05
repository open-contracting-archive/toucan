from functools import wraps

from dateutil import parser
from django.http import JsonResponse
from django.utils.translation import gettext as _


def clear_files(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        request.session['files'] = []
        return function(request, *args, **kwargs)

    return wrap


def require_files(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if 'files' not in request.session:
            return JsonResponse({'error': 'No files uploaded'}, status=400, reason='No files available for operation')
        return function(request, *args, **kwargs)

    return wrap


def published_date(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        published_date = request.GET.get('publishedDate', '')
        if published_date:
            try:
                parser.parse(published_date)
                kwargs['published_date'] = published_date
            except ValueError:
                kwargs['warnings'] = [
                    _('An invalid published date was submitted, and therefore ignored: %(date)s') % {
                        'date': published_date,
                    },
                ]
        return function(request, *args, **kwargs)

    return wrap


def split_size(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        split_size = request.GET.get('splitSize')
        if split_size is None or split_size.isdecimal():
            kwargs['size'] = int(split_size)
        else:
            msg = _('An invalid split size was submitted, and therefore ignored. Default value is used, split size: 1')
            if 'warnings' in kwargs:
                kwargs['warnings'].append([msg])
            else:
                kwargs['warnings'] = [msg]
        return function(request, *args, **kwargs)

    return wrap


def optional_args(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        encoding = request.GET.get('encoding', 'utf-8')
        try:
            teststr = "test"
            teststr.encode(encoding)
            kwargs['encoding'] = encoding
        except LookupError:
            msg = _('An invalid encoding was submitted, and therefore ignored. Default value is used, utf-8')
            if 'warnings' in kwargs:
                kwargs['warnings'].append([msg])
            else:
                kwargs['warnings'] = [msg]
        kwargs['pretty_json'] = request.GET.get('pretty-json') == 'true'
        return function(request, *args, **kwargs)

    return wrap
