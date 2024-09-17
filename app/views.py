from django.http import HttpResponse
from django.shortcuts import render
from urllib.parse import quote
import requests

def get_files(public_link):
    files = []
    response = requests.get(f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_link}')
    if response.status_code == 200:
        data = response.json()
        if '_embedded' in data and 'items' in data['_embedded']:
            files = data['_embedded']['items']
            for file in files:
                file['file_id'] = file.get('resource_id', '')
                file['download_url'] = file['file'] if 'file' in file else None
    else:
        print(f'Error: {response.status_code}')
    return files

def view_files(request):
    files = []
    public_link = ''
    if request.method == 'POST':
        public_link = request.POST.get('public_link')
        files = get_files(public_link)
    
    return render(request, 'index.html', {'files': files, 'public_link': public_link})


def download_file(request, file_id):
    public_link = request.GET.get('public_link')  # Получаем публичную ссылку из запроса

    resource_url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_link}'
    response = requests.get(resource_url)

    if response.status_code == 200:
        data = response.json()
        file_info = None
        if '_embedded' in data and 'items' in data['_embedded']:
            for item in data['_embedded']['items']:
                if item.get('resource_id') == file_id:
                    file_info = item
                    break

        if file_info:
            download_url = file_info.get('file') or file_info.get('public_url')

            if download_url:
                file_response = requests.get(download_url, stream=True)

                if file_response.status_code == 200:
                    file_name = file_info.get('name', f"file_{file_id}")
                    file_name = quote(file_name)

                    response = HttpResponse(file_response.content,
                                            content_type=file_response.headers.get('Content-Type'))
                    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    return response
                else:
                    return render(request, 'index.html', {'error': 'Ошибка при загрузке файла'})
            else:
                return render(request, 'index.html', {'error': 'Ссылка для скачивания не найдена'})
        else:
            return render(request, 'index.html', {'error': 'Файл не найден'})
    else:
        return render(request, 'index.html', {'error': f'Ошибка API: {response.status_code}'})