import logging

from datetime import datetime
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from ocdstoucan.settings import OCDS_TOUCAN_GOOGLE_API_CREDENTIALS_FILE
from default.data_file import DataFile

"""
Code based in the documentation here: https://developers.google.com/identity/protocols/oauth2/web-server

See also:

* Oauth2 protocol: https://developers.google.com/identity/protocols/oauth2/
* Credentials class docs: https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.credentials.html
* Flow class docs: https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html

"""

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

google_api_messages = {
    '_default': _('There was an issue when trying to upload the file to Google Drive, please try again later.'),
    'access_denied': _('There was an authorization issue when saving the file to Google Drive, please try again.')
}

mime_types = {
    '_default': 'application/zip',
    '.csv': 'text/csv',
    '.xlsx': 'application/vnd.google-apps.spreadsheet'
}


def upload_to_drive(request):

    datafile = DataFile(**request.session['google_drive_file'])
    credentials = get_credentials_from_session(request)

    try:
        if credentials:
            if credentials.expired:
                credentials.refresh(GoogleRequest())
                save_refresh_info(request, credentials)
        else:
            flow = Flow.from_client_secrets_file(OCDS_TOUCAN_GOOGLE_API_CREDENTIALS_FILE, SCOPES)
            flow.redirect_uri = request.build_absolute_uri('googleapi-auth-response')

            authorization_response = request.session['auth_response']
            flow.fetch_token(authorization_response=authorization_response)

            credentials = flow.credentials
            save_credentials_to_session(request, credentials)

        service = build('drive', 'v3', credentials=credentials)

        if datafile.ext in mime_types.keys():
            mime_type = mime_types[datafile.ext]
        else:
            mime_type = mime_types['_default']

        file_metadata = {
            'name': datafile.name,
            'mimeType': mime_type
        }
        media = MediaFileUpload(datafile.path, mimetype=mime_type, resumable=True)
        results = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        return JsonResponse({
            'authenticated': True,
            'status': 'success',
            'name': datafile.name,
            'url': "https://drive.google.com/file/d/" + results["id"]
        })

    except Exception as e:
        print(e)
        return JsonResponse({
            'status': 'failed',
            'message': google_api_messages['_default']
        }, status=500)


def get_credentials_from_session(request):
    if 'credentials' in request.session:
        info = request.session['credentials']
        credentials = Credentials(info['token'], refresh_token=info['refresh_token'],
                                  id_token=info['id_token'], token_uri=info['token_uri'],
                                  client_id=info['client_id'], client_secret=info['client_secret'],
                                  scopes=info['scopes'])

        credentials.expiry = datetime.utcfromtimestamp(info['expiry'])

        return credentials
    return None


def save_credentials_to_session(request, credentials):
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'id_token': credentials.id_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        'expiry': credentials.expiry.timestamp()
    }
    request.session.modified = True


def save_refresh_info(request, credentials):
    request.session['credentials']['token'] = credentials.token
    request.session['credentials']['expiry'] = credentials.expiry.timestamp()
