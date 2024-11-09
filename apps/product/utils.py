import requests
import os


def upload_image_to_api(image_path, **other_data):
    print("Subiendo imagen pá")
    api_url = 'https://api.imgur.com/3/image'
    headers = {
        'Authorization': f'Client-ID {os.environ.get("IMGUR_CLIENT_ID")}'
    }
    data = {
        'type': "file",
        'title': other_data['name'],
        'description': other_data['description'],
    }

    with open(image_path, 'rb') as image_file:
        files = {
            'image': image_file
        }
        response = requests.post(api_url, files=files,
                                 data=data, headers=headers)
        print(response)
    if response.status_code in [200, 201]:
        print(response.json().get('data').get('link'))
        return response.json().get('data').get('link')
    else:
        print("ERROR")
        raise Exception(
            f'Error al subir la imagen: {response.status_code} - {response.text}')
