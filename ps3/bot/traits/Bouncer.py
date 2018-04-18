# coding=utf-8
"""Module for keeping a matrix room member list in sync with a given list of mxids."""

import sqlite3

from ps3.util import Community
from ps3.bot.traits import Trait
from matrix_client.errors import MatrixRequestError

class Bouncer(Trait):
    """Makes sure a room member list matches a given list of mxids."""

    def __init__(self):
        self._database = sqlite3.connect('invites.db')

    def enforce_group(self, group, guests, actually_invite=False,
                      actually_kick=False, verbose=False):
        print
        print 'Bouncer: Syncing group membership: %s' % group
        community = Community(group)
        access_token = self.get_client().api.token

        members_and_invited_members = (community.members(access_token) +
                                       community.invited_users(access_token))

        for guest in guests:
            if guest not in members_and_invited_members:
                if actually_invite:
                    if verbose:
                        print 'Bouncer: Inviting %s to %s' % (guest, group),
                    else:
                        print '+%s' % guest,
                    try:
                        print community.invite(guest, access_token)
                    except Exception, e:
                        print e
                else:
                    if verbose:
                        print 'Bouncer: Would have invited %s to %s' % (guest, group)
                    else:
                        print '+%s' % guest

        for member in members_and_invited_members:
            if member not in guests:
                if actually_kick and member != '@patroniser:matrix.org':
                    if verbose:
                        print 'Bouncer: Kicking %s from %s' % (member, group),
                    else:
                        print '-%s' % member,
                    try:
                        print community.remove(guest, access_token)
                    except Exception, e:
                        print e
                else:
                    if verbose:
                        print 'Bouncer: Would have kicked %s from %s' % (member, group)
                    else:
                        print '-%s' % member

    def enforce(self, room_alias, guests, actually_invite=True,
                actually_kick=True, verbose=False):
        """Sync the membership of a room with a defined list."""
        print
        print 'Bouncer: Syncing room membership: %s' % room_alias
        room = self.get_client().join_room(room_alias)

        occupants = [user.user_id for user in room.get_joined_members()]

        to_invite = set(guests) - set(occupants)
        to_kick = set(occupants) - set(guests)

        for user in to_kick:
            if user != self.get_client().user_id:
                if actually_kick:
                    if verbose:
                        print 'Bouncer: Kicking %s from %s' % (user, room_alias)
                    else:
                        print '-%s' % user
                    try:
                        room.kick_user(user, reason='PatroniserBot thinks you\'re no longer entitled to access this room. If PatroniserBot is wrong, kindly let us know in #matrix:matrix.org. Thanks for your support!')
                    except KeyError, e:
                        if e.message == 'retry_after_ms':
                            if verbose:
                                print 'Bouncer: Failed to kick %s from %s - remote server 429ed us' % (user, room_alias)
                else:
                    if verbose:
                        print 'Bouncer: Would have kicked %s from %s' % (user, room_alias)
                    else:
                        print '-%s' % user

        database = sqlite3.connect('invites.db')

        already_invited = self._get_issued_invites(database)

        for user in to_invite:
            if (user, room.room_id) not in already_invited:
                if actually_invite:
                    print 'Bouncer: Inviting %s to %s' % (user, room_alias)
                    try:
                        self._invite(user, room, database)
                    except KeyError, e:
                        if e.message == 'retry_after_ms':
                            if verbose:
                                print 'Bouncer: Failed to invite %s to %s - remote server 429ed us' % (user, room_alias)
                    except MatrixRequestError, e:
                        print e

                else:
                    if verbose:
                        print 'Bouncer: Would have invited %s to %s' % (user, room_alias)
                    else:
                        print '+%s' % user
            else:
                if verbose:
                    print 'Bouncer: Politely not re-inviting %s to %s' % (user, room_alias)

    def _get_issued_invites(self, database):
        query = 'select mxid, roomid from invites'
        cursor = database.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [(row[0], row[1]) for row in rows]

    def _invite(self, user, room, database):
        self.get_client().api.invite_user(room.room_id, user)
        query = 'insert into invites (mxid, roomid) values (?, ?)'
        cursor = database.cursor()
        cursor.execute(query, (user, room.room_id, ))
        database.commit()
