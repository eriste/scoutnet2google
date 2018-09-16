"""Handle google auth with installed credentials."""
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from typing import List
import json


LOGGER = logging.getLogger(__name__)


def google_auth_installed(secret_file: str, token_file: str,
                          scopes: List[str]) -> Credentials:
    """Authenticate installed applications with Google."""
    try:
        with open(token_file, 'rt') as token_file_fd:
            token_data = json.load(token_file_fd)
        credentials = Credentials(
            None,
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
        )
    except Exception as exc:
        LOGGER.debug("Exception: %s", str(exc))
        flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes)
        credentials = flow.run_console()
        token_data = {
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
        }
        with open(token_file, 'wt') as token_file:
            json.dump(token_data, token_file)
        LOGGER.info("Credentials saved to %s", token_file)
    return credentials
