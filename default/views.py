from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'default/index.html')

def upgrade(request):
    return render(request, 'default/upgrade.html')

def uploadfile(request):
    r = {'files': []}
    if request.method == 'POST':
       uploadedfile = request.FILES['file']
       r['files'].append({
           'name': uploadedfile.name, 
           'size': uploadedfile.size
       })
    return JsonResponse(r)
