from django.contrib.auth import get_user

from Google import Create_Service
from googleapiclient.http import MediaFileUpload

from users.models import HOD, AuthUser


# CLIENT_SECRET_FILE = 'client_secrets.json'
# API_NAME = 'drive'
# API_VERSION = 'v3'
# SCOPES = ['https://www.googleapis.com/auth/drive']

# service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
# folder_id = '1ixUVcYrHr0NTy6HQ7ySqp9UDM09HsOJi'


def upload_file_to_drive(file_name, file_path, request):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype='application/pdf')

    file = service.files().create(body=file_metadata, media_body=media).execute()

    print('File ID: %s' % file.get('id'))
    print("File= ", file)
    return file.get('id')

def get_file_link(file_id):
    request_body = {
        'role': 'reader',
        'type': 'anyone'
    }
    request_permission = service.permissions().create(
        fileId=file_id, 
        body=request_body
    ).execute()
    print("Request Permission: ", request_permission)

    body = {'copyRequiresWriterPermission': True}
    response = service.files().update(
        fileId=file_id, 
        body=body,
    ).execute()
    print("Response: ", response)

    response_share_link = service.files().get(
        fileId=file_id, 
        fields='webViewLink'
    ).execute()
    web_view_link = response_share_link['webViewLink']
    print("Web View Link: ", web_view_link)

    return web_view_link

def remove_file_from_drive(file_id):
    service.files().delete(fileId=file_id).execute()
    print('File with ID %s has been removed from Google Drive' % file_id)




