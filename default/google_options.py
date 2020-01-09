from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload, MediaIoBaseDownload


def upload_option(file_name, file_path):
    creds = None
    # Setup the Drive v3 API
    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
    if not creds or not creds.valid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'mimeType': '*/*'
    }
    media = MediaFileUpload(file_path,
                            mimetype='*/*',
                            resumable=True)
    file_upload = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    id_file = file_upload.get('id')

    return id_file
