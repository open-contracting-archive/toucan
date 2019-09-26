from functools import wraps

from django.http import JsonResponse


def require_files(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if 'files' not in request.session:
            return JsonResponse({'error': 'No files uploaded'}, status=400, reason='No files available for operation')
        return function(request, *args, **kwargs)

    return wrap
