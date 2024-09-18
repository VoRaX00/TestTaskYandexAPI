

import aiohttp
from django.http import HttpResponse
from django.shortcuts import render
from urllib.parse import quote

async def get_files(public_link):
    files = []
    url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_link}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if 'type' in data and data['type'] == 'file':
                    files.append({
                        'file_id': data.get('resource_id', ''),
                        'name': data.get('name', ''),
                        'download_url': data.get('file', ''),
                    })
                elif '_embedded' in data and 'items' in data['_embedded']:
                    files = data['_embedded']['items']
                    for file in files:
                        file['file_id'] = file.get('resource_id', '')
                        file['download_url'] = file['file'] if 'file' in file else None
            else:
                print(f'Error: {response.status}')
    return files

async def view_files(request):
    files = []
    public_link = ''

    if request.method == 'POST':
        public_link = request.POST.get('public_link')
        files = await get_files(public_link)

    return render(request, 'index.html', {'files': files, 'public_link': public_link})


async def download_file_async(public_link, file_id):
    resource_url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_link}'
    async with aiohttp.ClientSession() as session:
        async with session.get(resource_url) as response:
            if response.status == 200:
                data = await response.json()
                file_info = None

                if 'type' in data and data['type'] == 'file' and data.get('resource_id') == file_id:
                    file_info = data
                elif '_embedded' in data and 'items' in data['_embedded']:
                    for item in data['_embedded']['items']:
                        if item.get('resource_id') == file_id:
                            file_info = item
                            break

                if file_info:
                    download_url = file_info.get('file') or file_info.get('public_url')
                    if download_url:
                        async with session.get(download_url) as file_response:
                            if file_response.status == 200:
                                file_name = file_info.get('name', f"file_{file_id}")
                                file_name = quote(file_name)
                                content = await file_response.read()

                                return HttpResponse(content, content_type=file_response.headers.get('Content-Type'), headers={
                                    'Content-Disposition': f'attachment; filename="{file_name}"'
                                }), None
                            else:
                                return None, 'Error downloading file'
                    else:
                        return None, 'Error not found link for download file'
                else:
                    return None, 'Error file not found'
            else:
                return None, f'Error: {response.status}'

async def download_files(request, file_id):
    public_link = request.GET.get('public_link')
    file_response, error = await download_file_async(public_link, file_id)

    if file_response:
        return file_response
    else:
        print(f'Error: {error}')
        return render(request, 'index.html')