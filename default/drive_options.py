import logging

from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauthlib.oauth2 import AccessDeniedError
from ocdstoucan.settings import OCDS_TOUCAN_CREDENTIALS_DRIVE

logger = logging.getLogger(__name__)

SCOPES = 'https://www.googleapis.com/auth/drive.file'


def upload_to_drive(filename, filepath, format=None, credentials=None):
    try:
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(OCDS_TOUCAN_CREDENTIALS_DRIVE, SCOPES)
                credentials = flow.run_local_server(
                    port=0,
                    success_message=_('The authentication flow has completed. You may close this window.'),
                    open_browser=True
                )
        service = build('drive', 'v3', credentials=credentials)

    except AccessDeniedError:
        return HttpResponse(_('Access denied'), status=400)

    try:
        if format == 'xlsx':
            mimeType = 'application/vnd.google-apps.spreadsheet'
        else:
            mimeType = 'application/zip'

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

    except:
        return HttpResponse(_('Upload failed'), status=400)
