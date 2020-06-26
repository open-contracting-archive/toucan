from django import template

from ocdstoucan import settings

register = template.Library()


@register.simple_tag
def google_api_client_id():
    if settings.OCDS_TOUCAN_GOOGLE_API_CREDENTIALS:
        return settings.OCDS_TOUCAN_GOOGLE_API_CREDENTIALS['web']['client_id']
