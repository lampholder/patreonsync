#!/usr/bin/env python3

import argparse

import yaml
from yaml import Loader

from ps3.bot import Patroniser
from ps3.subscribers import GuestListUtils, YamlGuestList
from ps3.subscribers.patreon import PatreonGuestList
from ps3.util.TokenRefresher import refresh_token

# sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

CONFIG_FILE = "config.yaml"

# Get a fresh set of oauth credentials every time. Don't leave it a month
# between executions else you'll have to get new tokens using the web UI at
# https://www.patreon.com/portal/registration/register-clients
refresh_token(CONFIG_FILE)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--do-room-invites",
        action="store_true",
        help="Using the credentials in config.yaml, patreonsync will read the current list of patrons from the Patreon account, compare that list to the list of members of the Matrix room listed in config.yaml, and invite any new patrons to that room.",
    )
    parser.add_argument(
        "--do-room-kicks",
        action="store_true",
        help="Using the credentials in config.yaml, patreonsync will read the current list of patrons from the Patreon account, compare that list to the list of members of the Matrix room listed in config.yaml, and kick any former patrons from that room.",
    )
    parser.add_argument(
        "--do-group-invites",
        action="store_true",
        help="Using the credentials in config.yaml, patreonsync will read the current list of patrons from the Patreon account, compare that list to the list of members of the Matrix group listed in config.yaml, and invite any new patrons to that group.",
    )
    parser.add_argument(
        "--do-group-kicks",
        action="store_true",
        help="Using the credentials in config.yaml, patreonsync will read the current list of patrons from the Patreon account, compare that list to the list of members of the Matrix group listed in config.yaml, and kick any former patrons from that group.",
    )
    parser.add_argument(
        "--createrooms",
        action="store_true",
        help="patreonsync will read the list of Matrix rooms from config.yaml, then, using the credentials in config.yaml, compare that list to the list of Matrix rooms in the Matrix account, and create any rooms that do not yet exist.",
    )
    parser.add_argument(
        "--skiplookup",
        action="store_true",
        help="I'm not exactly sure what this does, yet...",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="This option will print verbose output to the terminal and is useful when you are first setting up patreonsync. (It will do nothing if you are running patreonsync as an automated task.",
    )

    args = parser.parse_args()

    with open(CONFIG_FILE) as config_file:
        config = yaml.load(stream=config_file, Loader=Loader)

    # Load config:
    bot_user = config["matrix"]["user"]
    bot_password = config["matrix"]["password"]

    creator_access_token = config["patreon"]["creator_access_token"]
    campaign_id = config["patreon"]["campaign_id"]

    patroniser = Patroniser(bot_user, bot_password)

    patreon = PatreonGuestList(patroniser, creator_access_token).guest_list(
        campaign_id, skip_lookup=args.skiplookup, create_room=args.createrooms
    )
    manual = YamlGuestList("manual_subscribers.yaml").guest_list()
    staff = YamlGuestList("staff.yaml").guest_list()

    guest_list = GuestListUtils.aggregate([patreon, manual, staff])

    for room, guests in guest_list.iteritems():
        community_guests = [guest[0] for guest in guests if guest[1]]
        patroniser.enforce_group(
            room.replace("#", "+", 1),
            community_guests,
            actually_invite=args.do_group_invites,
            actually_kick=args.do_group_kicks,
            verbose=args.verbose,
        )

        room_guests = [guest[0] for guest in guests]
        patroniser.enforce(
            room,
            room_guests,
            actually_invite=args.do_room_invites,
            actually_kick=args.do_room_kicks,
            verbose=args.verbose,
        )

# get all the patrons
# see who we already know
# try and get mxids for the people we don't know
# sync the room membership
