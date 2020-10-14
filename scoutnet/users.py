"""Implements interface to Scoutnet mailinglists."""
import os
import requests
import logging
import json
from typing import List, Any, Dict
from dataclasses import dataclass, field
from appdirs import AppDirs
import functools
from dateutil.relativedelta import relativedelta
import datetime


DIRS = AppDirs('Scoutnet2Google', 'scoutnet2google')
DEFAULT_CONFIG_FILE = os.path.join(DIRS.user_config_dir, 'scoutnet2google.ini')


class lazy_property(object):
    '''
    meant to be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    '''

    def __init__(self, fget):
        self.fget = fget

        # copy the getter function's docstring and other attributes
        functools.update_wrapper(self, fget)

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = self.fget(obj)
        setattr(obj, self.fget.__name__, value)
        return value


@dataclass(frozen=True)
class ScoutnetUser:
    """Hold information about a Scoutnet user."""

    member_no: str
    first_name: str
    last_name: str
    email_primary: str
    email_alternate: str = None
    email_mum: str = None
    email_dad: str = None
    unit: str = None
    mobile: str = None
    date_of_birth: str = None
    role: str = None


class ScoutnetUsersApi(object):
    """Access Scoutnet users api."""

    def __init__(self, api_endpoint: str, api_id: str, api_key: str) -> None:
        """Initialize."""
        self.endpoint = api_endpoint
        self.session = requests.Session()
        self.session.auth = (api_id, api_key)
        self.logger = logging.getLogger(__name__)

    def memberlist(self) -> Any:
        """Get the configured users."""
        response = self.session.get('{}/group/memberlist'.format(
            self.endpoint))
        response.raise_for_status()
        return response.json()['data']

    def get_all_users(self) -> List[ScoutnetUser]:
        """Fetch all users from Scoutnet."""
        users = []
        for (clist, cdata) in self.memberlist().items():
            def get_value(data, key):
                if key in data:
                    return data[key]['value']
                else:
                    return None
            users.append(
                ScoutnetUser(
                    get_value(cdata, 'member_no'),
                    first_name=get_value(cdata, 'first_name'),
                    last_name=get_value(cdata, 'last_name'),
                    email_primary=get_value(cdata, 'email'),
                    email_alternate=get_value(cdata, 'contact_alt_email'),
                    email_dad=get_value(cdata, 'contact_email_dad'),
                    email_mum=get_value(cdata, 'contact_email_mum'),
                    unit=get_value(cdata, 'unit'),
                    mobile=get_value(cdata, 'contact_mobile_phone'),
                    date_of_birth=get_value(cdata, 'date_of_birth'),
                    role=get_value(cdata, 'group_role')))
        return users

    @lazy_property
    def all_users(self):
        """All users."""
        return self.get_all_users()

    @lazy_property
    def all_adults(self):
        """All users at least 18 years of age."""
        adults = []
        today = datetime.date.today()
        for user in self.all_users:
            bday = datetime.datetime.strptime(user.date_of_birth, '%Y-%m-%d')
            age = relativedelta(today, bday).years
            if age >= 18:
                adults.append(user)
        return adults

    def all_unit_members(self, unit):
        """All users who belong to a unit."""
        members = []
        for user in self.all_users:
            if user.unit == unit:
                members.append(user)

        return members

    def subtract_list(self, source, substract):
        """Subtract members from subtract from source."""
        submembers = [member.member_no for member in substract]
        return [member for member in source if member.member_no not in submembers]