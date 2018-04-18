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
        """Return a dict of room names to tuples of (entitled members, a flag
        indicating whether this is the top tier they qualify for)"""

        guest_list = {reward.room_alias: [] for reward in REWARDS}

        for patron in self._client.patrons(campaign_id):
            top_reward_tier = max([reward for reward in REWARDS
                                   if patron.amount >= reward.minimum_donation],
                                  key=lambda r: r.minimum_donation)
            for reward in REWARDS:
                if patron.active and patron.amount >= reward.minimum_donation:
                    guest_list[reward.room_alias].append((patron,
                                                          reward==top_reward_tier))

        return guest_list

    def guest_list(self, campaign_id, skip_lookup=False, create_room=True,
                   verbose=False):

        mxid_guest_list = defaultdict(list)

        # Resolving guests via Matrix is s l o w; we end up doing it for each
        # instance of the guest for each room they're entitled to be in.
        # Rather than do the obvious restructuring this could benefit from,
        # let's just track the guests we've already looked up via Matrix once
        # this go and not bother to look them up again.
        looked_up_guests = []

        for room, guests in self._patreon_users_guest_list(campaign_id).iteritems():
            for (guest, is_top_tier) in guests:
                mxids = self._address_book.get_mxids(guest.pid)
                if len(mxids) > 0:
                    print 'PA: Found Patreon "%s" in address book; resolved to %s' % (guest.name, ','.join(mxids))
                    for mxid in mxids:
                        mxid_guest_list[room].append((mxid, is_top_tier))
                elif skip_lookup:
                    print 'PA: Couldn\'t find Patreon "%s" in address book; skipping matrix lookup' % guest.name
                elif guest.pid in looked_up_guests:
                    print 'PA: Couldn\'t find Patreon "%s" in address book; already looked up via Matrix this session so skipping for now.' % guest.name
                else:
                    print 'PA: Couldn\'t find Patreon "%s" in address book; resolving via matrix...' % guest.name
                    looked_up_guests.append(guest.pid)
                    mxid = self._patroniser_bot.get_mxid_from_patron(guest, create_room=create_room)
                    if mxid != None:
                        print 'PA: Newly resolved Patreon "%s" to %s' % (guest.name, mxid)
                        self._address_book.add(guest.pid, mxid)
                        mxid_guest_list[room].append((mxid, is_top_tier))
                    else:
                        print 'PA: Patreon "%s" has not yet joined their lookup room.' % guest.name

        return mxid_guest_list


