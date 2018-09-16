"""Implement acceess to Scoutnet."""
from scoutnet import *

from .mailinglists import ScoutnetMailinglist, ScoutnetMailinglistApi

DEFAULT_CONFIG_SCOUTNET = {
    'api_endpoint': 'https://www.scoutnet.se/api',
    'api_id': '',
    'api_key_groups': '',
    'api_key_users': ''
}
