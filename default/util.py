import json
import logging

from django.utils.translation import gettext_lazy as _
from ocdskit.util import is_record_package, is_release_package, json_loads

logger = logging.getLogger(__name__)


def file_is_valid(file, ocds_type=None):
    try:
        data = json_loads(file.read())
        if ocds_type == 'release-package':
            if not is_release_package(data):
                return False, _('Not a release package')
        elif ocds_type == 'record-package':
            if not is_record_package(data):
                return False, _('Not a record package')
        return True, ''
    except json.JSONDecodeError:
        logger.debug('Error decoding file {}'.format(file.name))
        return False, _('Error decoding json')
