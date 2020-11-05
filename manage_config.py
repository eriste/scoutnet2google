"""Manage config."""
import os
import sys
import configparser
import logging
from appdirs import AppDirs

DIRS = AppDirs('Scoutnet2Google', 'scoutnet2google')
DEFAULT_CONFIG_FILE = os.path.join(DIRS.user_config_dir, 'scoutnet2google.ini')

DEFAULT_CONFIG_GOOGLE = {
    'auth': 'standalone',
    'domain': '',
}

DEFAULT_CONFIG = """
[scoutnet]
api_endpoint: https://www.scoutnet.se/api
api_id: 
api_key_groups: 
api_key_users: 
youthgroup_with_accounts =

[google]
auth: installed
domain: example.com
"""

class S2g_config(configparser.ConfigParser):
    """Scoutnet2google config."""
    def __init__(self, config_file:str = DEFAULT_CONFIG_FILE):
        """Open config."""
        super().__init__()
        self.read_string(DEFAULT_CONFIG)
        self.read(DEFAULT_CONFIG_FILE)

    def getlist(self, section: str, entry: str) -> list:
        """Return entry as a list."""
        return self[section][entry].split('\n')
