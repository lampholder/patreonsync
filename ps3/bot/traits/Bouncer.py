# coding=utf-8
"""Module for keeping a matrix room member list in sync with a given list of mxids."""

import sqlite3

from ps3.bot.traits import Trait

class Bouncer(Trait):
    """Makes sure a room member list matches a given list of mxids."""

    def __init__(self):
        self._database = sqlite3.connect('invites.db')

    def enforce(self, room_alias, guests, actually_invite=True, actually_kick=True):
        """Sync the membership of a room with a defined list."""
        print 'Bouncer: Syncing membership of %s' % room_alias
        room = self.get_client().join_room(room_alias)

        occupants = [user.user_id for user in room.get_joined_members()]

        to_invite = set(guests) - set(occupants)
        to_kick = set(occupants) - set(guests)

        for user in to_kick:
            if user != self.get_client().user_id:
                if actually_kick:
                    print 'Bouncer: Kicking %s from %s' % (user, room_alias)
                    room.kick_user(user, reason='PatroniserBot thinks you\'re no longer entitled to access this room. If PatroniserBot is wrong, kindly let us know in #matrix:matrix.org. Thanks for your support!')
                else:
                    print 'Bouncer: Would have kicked %s from %s' % (user, room_alias)

        database = sqlite3.connect('invites.db')

        already_invited = self._get_issued_invites(database)

        for user in to_invite:
            if (user, room.room_id) not in already_invited:
                if actually_invite:
                    print 'Bouncer: Inviting %s to %s' % (user, room_alias)
                    self._invite(user, room, database)
                else:
                    print 'Bouncer: Would have invited %s to %s' % (user, room_alias)
            else:
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
