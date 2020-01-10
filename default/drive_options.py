from __future__ import print_function
from django.http import HttpResponse
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import UnknownFileType
from googleapiclient.http import MediaFileUpload
from oauthlib.oauth2 import AccessDeniedError
from ocdstoucan.settings import OCDS_TOUCAN_CREDENTIALS_DRIVE


def upload_to_drive(filename, filepath, format=None):
    try:
        credentials = None
        SCOPES = 'https://www.googleapis.com/auth/drive.file'
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    OCDS_TOUCAN_CREDENTIALS_DRIVE, SCOPES)
                credentials = flow.run_local_server(port=0)
        service = build('drive', 'v3', credentials=credentials)

    except AccessDeniedError:
        return HttpResponse('Access Denied to Google Drive', status=400)

    try:
        if format == 'xlsx':
            mimeType = 'application/vnd.google-apps.spreadsheet'
        else:
            mimeType = '*/*'

        file_metadata = {
            'name': filename,
            'mimeType': mimeType
        }
        media = MediaFileUpload(filepath,
                                mimetype=mimeType,
                                resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        return HttpResponse('Uploaded to Google Drive: Check your account', status=200)

    except (TypeError, Exception, IOError, UnknownFileType):
        return HttpResponse('Fail uploading to Google Drive', status=400)
