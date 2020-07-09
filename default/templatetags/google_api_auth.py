import json
import os

from django import template
from django.core.cache import cache

from ocdstoucan import settings

register = template.Library()


def _read_file_contents():
    with open(settings.OCDS_TOUCAN_GOOGLE_API_CREDENTIALS_FILE) as f:
        return json.load(f)


@register.simple_tag
def google_api_client_id():
    if settings.OCDS_TOUCAN_GOOGLE_API_CREDENTIALS_FILE and \
            os.path.isfile(settings.OCDS_TOUCAN_GOOGLE_API_CREDENTIALS_FILE):
        return cache.get_or_set('drive_client_id', _read_file_contents()['web']['client_id'], None)
