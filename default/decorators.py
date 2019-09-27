import logging
from dateutil import parser
from functools import wraps

from django.http import JsonResponse

logger = logging.getLogger(__name__)


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
                # invalid date has been received
                # TODO send a warning to client side
                logger.debug('Invalid date submitted: {}, ignoring'.format(published_date))
        return function(request, *args, **kwargs)

    return wrap
