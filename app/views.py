from django.shortcuts import render

def view_files(request):
    return render(request, 'index.html')

def download_file(request):
    return render(request, 'index.html')
