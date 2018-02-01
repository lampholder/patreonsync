# coding=utf-8
"""Handles communication with Patreon in order to sync subscriber tiers with Matrix room/groups."""

import datetime
from collections import namedtuple

import patreon

Patron = namedtuple('Patron', ['pid',      # Patreon subscriber id
                               'name',     # full name
                               'email',    # Patreon email address
                               'amount',   # subscription value (in cents)
                               'active',   # false if the most recent billing failed
                               'lifetime', # days since signing up
                               'lapsed'])  # days since failed bill attempt

class Patreon(object):
    """Class for fetching Patreon patron details in a useful way."""

    def __init__(self, access_token):
        self._api = patreon.API(access_token)

    def patrons(self, campaign_id):
        """Translate the json patron/pledge objects into a useful representation of
        patron status"""
        (users, pledges) = self._fetch_user_pledges(campaign_id)
        patrons = []

        def days_since(date_field):
            """Converts a string date to a date object and calculates the delta from today"""
            return ((datetime.datetime.today()
                     - datetime.datetime.strptime(date_field[:19], '%Y-%m-%dT%H:%M:%S')).days
                    if date_field is not None
                    else 0)

        user_dir = {user['id']: user for user in users}
        for pledge in pledges:
            patreon_id = pledge['relationships']['patron']['data']['id']
            user = user_dir[patreon_id]
            patrons.append(Patron(pid=patreon_id,
                                  name=user['attributes']['full_name'],
                                  email=user['attributes']['email'],
                                  amount=pledge['attributes']['amount_cents'],
                                  active=pledge['attributes']['declined_since'] is None,
                                  lifetime=days_since(pledge['attributes']['created_at']),
                                  lapsed=days_since(pledge['attributes']['declined_since'])))
        return patrons

    def _fetch_page_of_pledges(self, campaign_id, batch_size):
        """Uses the API, and does some error handling, because sometimes that is good to do
        PATREON *ahem*"""
        response = self._api.fetch_page_of_pledges(campaign_id, batch_size)
        if isinstance(response, dict) and 'errors' in response:
            error = response['errors'][0]
            raise Exception('%s: %s - %s' % (error['status'], error['title'], error['detail']))
        else:
            return response.json_data

    def _fetch_user_pledges(self, campaign_id, batch_size=100):
        """Use the paginated Patreon library to pull back all of the patrons+pledges"""
        users = []
        pledges = []

        jsonapi_doc = self._fetch_page_of_pledges(campaign_id, batch_size)

        while True:
            users += [entity for entity in jsonapi_doc['included']
                      if 'type' in entity
                      and entity['type'] == 'user']
            pledges += [entity for entity in jsonapi_doc['data']
                        if 'type' in entity and entity['type'] == 'pledge']

            if 'next' in jsonapi_doc['links']:
                # There's a bug in the patreon library where it rejects a unicode object
                # because it is not a string :\
                jsonapi_doc['links']['next'] = jsonapi_doc['links']['next'].encode('ascii',
                                                                                   'ignore')
                cursor = self._api.extract_cursor(jsonapi_doc)
                jsonapi_doc = self._api.fetch_page_of_pledges(campaign_id, 100, cursor).json_data
            else:
                return (users, pledges)
