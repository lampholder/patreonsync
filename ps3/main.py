# -*- coding: utf-8 -*-

import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import yaml
import argparse

from ps3.bot import Patroniser
from ps3.subscribers import GuestListUtils

from ps3.subscribers.patreon import PatreonGuestList
from ps3.subscribers.patreon import PatreonGroupGuestList
from ps3.subscribers import YamlGuestList

from ps3.util.TokenRefresher import refresh_token

CONFIG_FILE = 'config.yaml'

# Get a fresh set of oauth credentials every time. Don't leave it a month
# between executions else you'll have to get new tokens using the web UI at
# https://www.patreon.com/portal/registration/register-clients 
refresh_token(CONFIG_FILE)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--do-room-invites', action='store_true')
    parser.add_argument('--do-room-kicks', action='store_true')
    parser.add_argument('--do-group-invites', action='store_true')
    parser.add_argument('--do-group-kicks', action='store_true')
    parser.add_argument('--createrooms', action='store_true')
    parser.add_argument('--skiplookup', action='store_true')
    parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args()

    config = yaml.load(open(CONFIG_FILE, 'r'))

    # Load config:
    bot_user = config['matrix']['user']
    bot_password = config['matrix']['password']

    creator_access_token = config['patreon']['creator_access_token']
    campaign_id = config['patreon']['campaign_id']


    patroniser = Patroniser(bot_user, bot_password)

    patreon = PatreonGuestList(patroniser,
                               creator_access_token).guest_list(campaign_id,
                                                                skip_lookup=args.skiplookup,
                                                                create_room=args.createrooms)
    manual = YamlGuestList('manual_subscribers.yaml').guest_list()
    staff = YamlGuestList('staff.yaml').guest_list()

    guest_list = GuestListUtils.aggregate([patreon,
                                           manual,
                                           staff])

    for room, guests in guest_list.iteritems():
        community_guests = [guest[0] for guest in guests if guest[1]]
        patroniser.enforce_group(room.replace('#', '+', 1),
                                 community_guests,
                                 actually_invite=args.do_group_invites,
                                 actually_kick=args.do_group_kicks,
                                 verbose=args.verbose)

        room_guests = [guest[0] for guest in guests]
        patroniser.enforce(room, room_guests,
                           actually_invite=args.do_room_invites,
                           actually_kick=args.do_room_kicks,
                           verbose=args.verbose)

# get all the patrons
# see who we already know
# try and get mxids for the people we don't know
# sync the room membership
