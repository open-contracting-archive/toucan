from __future__ import print_function
from django.http import HttpResponse, JsonResponse
from google.auth.exceptions import DefaultCredentialsError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import UnknownFileType
from googleapiclient.http import MediaFileUpload
from oauthlib.oauth2 import AccessDeniedError
from ocdstoucan.settings import OCDS_TOUCAN_CREDENTIALS_DRIVE


SCOPES = 'https://www.googleapis.com/auth/drive.file'


def upload_to_drive(filename, filepath, format=None, test=None, credentials=None):
    try:
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    OCDS_TOUCAN_CREDENTIALS_DRIVE, SCOPES)
                if not test:
                    credentials = flow.run_local_server(port=0)
                if credentials and not credentials.valid:
                    raise AccessDeniedError
        service = build('drive', 'v3', credentials=credentials)

    except AccessDeniedError:
        return HttpResponse("Access Denied", status=400)

    except DefaultCredentialsError:
        service = None

    try:
        if format == 'xlsx':
            mimeType = 'application/vnd.google-apps.spreadsheet'
        else:
            if format == 'csv' or format is None:
                mimeType = 'application/zip'
            else:
                mimeType = '*/*'

        file_metadata = {
            'name': filename,
            'mimeType': mimeType
        }
        media = MediaFileUpload(filepath,
                                mimetype=mimeType,
                                resumable=True)
        results = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        return JsonResponse({
            'name': filename,
            'id': results["id"]
        })

    except (TypeError, Exception, IOError, UnknownFileType):
        if test:
            return HttpResponse("Test", status=200)
        else:
            return HttpResponse("Fail Uploading", status=400)
