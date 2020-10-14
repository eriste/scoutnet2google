"""Handle the config file from command line."""
import configparser
import os
from appdirs import AppDirs
from scoutnet import DEFAULT_CONFIG_SCOUTNET


DIRS = AppDirs('Scoutnet2Google', 'scoutnet2google')
DEFAULT_CONFIG_FILE = os.path.join(DIRS.user_config_dir, 'scoutnet2google.ini')

DEFAULT_CONFIG_GOOGLE = {
    'auth': 'standalone',
    'domain': '',
}

DEFAULT_CONFIG = """
[scoutnet]
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
    def __init__(self):
        """Open config."""
        super().__init__()
        self.read_string(DEFAULT_CONFIG)
        self.read(DEFAULT_CONFIG_FILE)

    def getlist(self, section: str, entry: str) -> list:
        """Return entry as a list."""
        return self[section][entry].split('\n')