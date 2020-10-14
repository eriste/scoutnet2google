"""Implements interface to Scoutnet mailinglists."""
import os
import requests
import logging
import json
from typing import List, Any, Dict
from dataclasses import dataclass, field
from appdirs import AppDirs


DIRS = AppDirs('Scoutnet2Google', 'scoutnet2google')
DEFAULT_CONFIG_FILE = os.path.join(DIRS.user_config_dir, 'scoutnet2google.ini')


@dataclass(frozen=True)
class ScoutnetMailinglist:
    """Hold information about a Scoutnet mailinglist."""

    id: str
    title: str = None
    description: str = None
    aliases: List[str] = field(default_factory=list)
    members: List[str] = field(default_factory=list)


class ScoutnetMailinglistApi(object):
    """Access Scoutnet mailinglists api."""

    def __init__(self, api_endpoint: str, api_id: str, api_key: str,
                 domain: str) -> None:
        """Initialize."""
        self.endpoint = api_endpoint
        self.session = requests.Session()
        self.session.auth = (api_id, api_key)
        self.domain = domain
        self.logger = logging.getLogger(__name__)

    def customlists(self) -> Any:
        """Get the configured customlists."""
        response = self.session.get('{}/group/customlists'.format(
            self.endpoint))
        return response.json()

    def get_list(self, list_data: dict) -> ScoutnetMailinglist:
        """Get information about a list."""
        url = list_data.get('link')
        response = self.session.get(url).json()
        email_addresses = set()
        data: Dict[str, Any] = response.get('data')
        title = list_data.get('title')
        if len(data) > 0:
            for (_, member_data) in data.items():
                if 'email' in member_data:
                    email = member_data['email']['value']
                    email_addresses.add(email.lower())
                else:
                    email = None
                self.logger.debug("Adding member %s (%s %s) to list \"%s\"",
                                  email,
                                  member_data['first_name']['value'],
                                  member_data['last_name']['value'],
                                  title)
                if 'extra_emails' in member_data:
                    extra_emails = member_data['extra_emails']['value']
                    for extra_mail in extra_emails:
                        email_addresses.add(extra_mail.lower())
                        self.logger.debug("Additional address %s for user %s",
                                          extra_mail, email)
        list_aliases = list_data.get('aliases', {})
        aliases = []
        if len(list_aliases) > 0:
            for alias in list(set(list_aliases.values())):
                if alias.endswith('@' + self.domain):
                    aliases.append(alias)
                else:
                    self.logger.error("Invalid domain in alias: %s", alias)
        return ScoutnetMailinglist(id=list_data['list_email_key'],
                                   members=list(email_addresses),
                                   aliases=aliases,
                                   title=title,
                                   description=list_data.get('description'))

    def get_all_lists(self, limit: int = None) -> List[ScoutnetMailinglist]:
        """Fetch all mailing lists from Scoutnet."""
        all_lists = []
        count = 0
        for (clist, cdata) in self.customlists().items():
            count += 1
            mlist = self.get_list(cdata)
            self.logger.info("Fetched %s: %s (%d members)",
                             mlist.id, mlist.title, len(mlist.members))
            if len(mlist.aliases) > 0:
                self.logger.debug("Including %s: %s", mlist.id, mlist.title)
                all_lists.append(mlist)
            else:
                self.logger.debug("Excluding %s: %s", mlist.id, mlist.title)
            if limit is not None and count >= limit:
                break
        return all_lists
