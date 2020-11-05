"""Check that only Scoutnet users exist in Google."""
from typing import List, Any
import argparse
import logging
import os
from dataclasses import dataclass
import googleapiclient.discovery
import google.auth.compute_engine

from scoutnet2google.google_auth_installed import google_auth_installed
from scoutnet2google.scoutnet import ScoutnetUsersApi
from scoutnet2google import manage_config

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user",
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
]
API_SERVICE_NAME = "admin"
API_VERSION = "directory_v1"

CLIENT_SECRETS_FILE = os.path.join(
    manage_config.DIRS.user_config_dir, "client_secret_%s.json" % "check_users"
)
CLIENT_TOKEN_FILE = os.path.join(
    manage_config.DIRS.user_config_dir, "client_token_%s.json" % "check_users"
)


@dataclass(frozen=True)
class GoogleUser:
    """Hold information about a Google user."""

    first_name: str
    last_name: str
    email_primary: str
    email_alternate: str = None
    email_mum: str = None
    email_dad: str = None
    unit: str = None
    mobile: str = None


class GoogleUsersDirectory(object):
    """Access Google users directory."""

    def __init__(self, service: Any, domain: str, readonly: bool = False) -> None:
        """Initialize."""
        self.service = service
        self.domain = domain
        self.readonly = readonly
        self.logger = logging.getLogger("GoogleDirectory")
        if self.readonly:
            self.logger = self.logger.getChild("READONLY")
        self.all_users = self.get_all_users()

    def _compare_user(self, sn_user, g_user):
        """Check if a Scoutnet user and a Google user are the same."""
        return (
            g_user.first_name == sn_user.first_name
            and g_user.last_name == sn_user.last_name
        )

    def scoutnet_missing_in_google(self, scoutnet_users) -> [GoogleUser]:
        """Look for Scoutnet users missing in Google."""
        result = set()
        for sn_user in scoutnet_users:
            matches = [
                g_user
                for g_user in self.all_users
                if self._compare_user(sn_user, g_user)
            ]
            if len(matches) == 0:
                result.add(sn_user)
        return list(result)

    def google_missing_in_scoutnet(self, scoutnet_users) -> [GoogleUser]:
        """Look for Google users missing in Scoutnet."""
        result = set()
        for g_user in self.all_users:
            matches = [
                sn_user
                for sn_user in scoutnet_users
                if self._compare_user(sn_user, g_user)
            ]
            if len(matches) == 0:
                logging.info("Failed to find match for %s", g_user)
                result.add(g_user)
        return list(result)

    def get_all_users(self) -> [GoogleUser]:
        """Get all users."""
        all_users: List[GoogleUser] = []
        token = None

        def pick_mobile(data):
            """Extract the mobile number."""
            mobiles = [phone["value"] for phone in data if phone["type"] == "mobile"]
            if len(mobiles) == 0:
                return None
            else:
                return mobiles[0]

        while True:
            result = (
                self.service.users().list(domain=self.domain, pageToken=token).execute()
            )
            for user in result.get("users", []):
                new_user = GoogleUser(
                    first_name=user["name"]["givenName"],
                    last_name=user["name"]["familyName"],
                    email_primary=user["primaryEmail"],
                    mobile=pick_mobile(user.get("phones", [])),
                )
                all_users.append(new_user)
            token = result.get("nextPageToken")
            if token is None:
                break
        return all_users


def print_sn_user(user, indent=2):
    """Print name of a user."""
    print("%s%-20.20s %-15.15s" % (" " * indent, user.last_name, user.first_name))


def main() -> None:
    """main."""
    parser = argparse.ArgumentParser(
        description="Check that only Scoutnet users exist in Google."
    )

    parser.add_argument(
        "--verbose", dest="verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help="Enable debugging output"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
        logging.getLogger("googleapiclient.discovery").setLevel(logging.WARNING)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.DEBUG)
        logging.getLogger("googleapiclient.discovery").setLevel(logging.DEBUG)

    config = manage_config.S2g_config()

    # Authenticate with Google
    assert config["google"]["auth"] in [
        "installed",
        "compute_engine",
    ], "Invalid authentication method"
    if config["google"]["auth"] == "installed":
        credentials = google_auth_installed(
            CLIENT_SECRETS_FILE, CLIENT_TOKEN_FILE, SCOPES
        )
    else:
        credentials = google.auth.compute_engine.Credentials()
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials, cache_discovery=False
    )
    directory = GoogleUsersDirectory(service, config["google"]["domain"])
    all_users = directory.get_all_users()

    # Configure Scoutnet
    scoutnet = ScoutnetUsersApi(
        api_endpoint=config["scoutnet"]["api_endpoint"],
        api_id=config["scoutnet"]["api_id"],
        api_key=config["scoutnet"]["api_key_users"],
    )
    all_active_adults = [
        member
        for member in scoutnet.all_adults
        if member not in scoutnet.all_unit_members("Övriga kårmedlemmar")
    ]

    youth_units = config.getlist("scoutnet", "youthgroup_with_accounts")
    logging.warning(
        'Adding members of "%s" as youth members.' % ('", "'.join(youth_units))
    )
    tmp = sum([scoutnet.all_unit_members(unit) for unit in youth_units], [])
    youths = scoutnet.subtract_list(tmp, all_active_adults)
    print(
        "Google: %d users, Scoutnet: %d users (%d adults, %d youths)"
        % (
            len(all_users),
            len(all_active_adults) + len(youths),
            len(all_active_adults),
            len(youths),
        )
    )

    # Check for Scoutnet users missing from Google.
    scoutnet_missing_in_google = directory.scoutnet_missing_in_google(
        all_active_adults + youths
    )
    print("Scoutnet users missing in Google: %d" % len(scoutnet_missing_in_google))
    for user in scoutnet_missing_in_google:
        print_sn_user(user)

    # Check for Scoutnet users missing from Google.
    google_missing_in_scoutnet = directory.google_missing_in_scoutnet(
        all_active_adults + youths
    )
    print("Google users missing in Scoutnet: %d" % len(google_missing_in_scoutnet))
    for user in google_missing_in_scoutnet:
        print_sn_user(user)

    # Syncronize with Google Directory
    # if not args.skip_google:
    #     # noinspection PyUnboundLocalVariable
    #     directory.sync_groups(all_groups)


if __name__ == "__main__":
    main()
