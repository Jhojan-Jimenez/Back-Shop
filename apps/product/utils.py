import requests
import os


def upload_image_to_api(image_path, **other_data):
    api_url = 'https://api.imgur.com/3/image'
    headers = {
        'Authorization': f'Client-ID {os.environ.get("IMGUR_CLIENT_ID")}'
    }
    data = {
        'type': "file",
        'title': other_data['name'],
        'description': other_data['description'],
    }
    try:
        files = {
            'image': image_path
        }
        response = requests.post(api_url, files=files,
                                 data=data, headers=headers)
        return response
    except Exception as e:
        print(e)
