# coding=utf-8
"""Module for exposing patreon subscribers as a list of rooms and mxids entitled to those rooms."""

from collections import namedtuple
from collections import defaultdict

from ps3.addressbook.AddressBook import AddressBook
from ps3.subscribers.patreon.PatreonClient import Patreon

Reward = namedtuple('Reward', ['room_alias',
                               'minimum_donation'])

REWARDS = [Reward('#linear-supporters:matrix.org', 100),
           Reward('#quadratic-supporters:matrix.org', 500),
           Reward('#polynomial-supporters:matrix.org', 1000),
           Reward('#elliptic-supporters:matrix.org', 5000)]

class PatreonGuestList(object):
    """Filters patreon users into room guest lists."""

    def __init__(self, patroniser_bot, creator_access_token):
        self._patroniser_bot = patroniser_bot
        self._client = Patreon(creator_access_token)
        self._address_book = AddressBook()

    def _patreon_users_guest_list(self, campaign_id):
        """Return a dict of room names to entitled members"""

        guest_list = {reward.room_alias: [] for reward in REWARDS}

        for patron in self._client.patrons(campaign_id):
            for reward in REWARDS:
                if patron.active and patron.amount >= reward.minimum_donation:
                    guest_list[reward.room_alias].append(patron)

        return guest_list

    def guest_list(self, campaign_id, skip_lookup=False, create_room=True):

        mxid_guest_list = defaultdict(list)

        for room, guests in self._patreon_users_guest_list(campaign_id).iteritems():
            for guest in guests:
                mxids = self._address_book.get_mxids(guest.pid)
                if len(mxids) > 0:
                    print 'PA: Found Patreon "%s" in address book; resolved to %s' % (guest.name, ','.join(mxids))
                    for mxid in mxids:
                        mxid_guest_list[room].append(mxid)
                elif skip_lookup:
                    print 'PA: Couldn\'t find Patreon "%s" in address book; skipping matrix lookup' % guest.name
                else:
                    print 'PA: Couldn\'t find Patreon "%s" in address book; resolving via matrix...' % guest.name
                    mxid = self._patroniser_bot.get_mxid_from_patron(guest, create_room=create_room)
                    if mxid != None:
                        print 'PA: Newly resolved Patreon "%s" to %s' % (guest.name, mxid)
                        self._address_book.add(guest.pid, mxid)
                        mxid_guest_list[room].append(mxid)
                    else:
                        print 'PA: Patreon "%s" has not yet joined their lookup room.' % guest.name

        return mxid_guest_list


