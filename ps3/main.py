# -*- coding: utf-8 -*-

import yaml
import argparse

from ps3.bot import Patroniser
from ps3.subscribers import GuestListUtils

from ps3.subscribers.patreon import PatreonGuestList
from ps3.subscribers import YamlGuestList

CONFIG_FILE = 'config.yaml'

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--doinvites', action='store_true')
    parser.add_argument('--dokicks', action='store_true')
    parser.add_argument('--createrooms', action='store_true')
    parser.add_argument('--skiplookup', action='store_true')

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
        patroniser.enforce(room, guests,
                           actually_invite=args.doinvites,
                           actually_kick=args.dokicks)

# get all the patrons
# see who we already know
# try and get mxids for the people we don't know
# sync the room membership
