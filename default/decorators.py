from django.http import JsonResponse

def require_files(func):
    def wrap(request, *args, **kwargs):
        if not 'files' in request.session:
            return JsonResponse({'error': 'No files uploaded'}, status=424, reason='No files available for operation')
        return func(request, *args, **kwargs)
    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
