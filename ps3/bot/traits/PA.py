# coding=utf-8
"""Module for tracking down an association between a threepid and a mxid."""

import sqlite3

from ps3.util import Matrix
from ps3.bot.traits import Trait

WELCOME_MESSAGE = """Hi there!
I'm the Patreon subscriber sync bot; I created this room to reconcile your patreon email address with your Matrix ID. If you're reading this message then your Patreon account and your Matrix ID are now linked - congratulations! You can now leave this room :)
If you have any questions, if you would like to link your Patreon account with a different Matrix ID, or if you think this link has been established in error, please contact @tom:lant.uk.
Thanks again for your support!"""

class PA(Trait):
    """Reaches out to potential invitees."""

    def get_or_create_room(self, patron, create_room=True):
        """Check in the room list store - if we've already set up a DM with this patreon,
        use it - otherwise create a fresh one."""
        database = sqlite3.connect('rooms.db')
        query = 'select room_id from patreon_room where patreon_id = ?'
        cursor = database.cursor()
        cursor.execute(query, (patron.pid,))
        rows = cursor.fetchall()
        if len(rows) == 1:
            print 'PA: Identified pre-existing room for %s' % patron.email
            return self.get_client().join_room(rows[0][0])
        elif create_room:
            print 'PA: Creating new room for %s' % patron.email
            room = self.get_client().create_room(is_public=False)
            query = 'insert into patreon_room (patreon_id, room_id) values (?, ?)'
            cursor.execute(query, (patron.pid, room.room_id))
            print 'PA: Inviting %s' % patron.email, Matrix.invite_threepid_user(self.get_client(), room.room_id, patron.email)
            room.send_text(WELCOME_MESSAGE)
            database.commit()
            return room
        else:
            print 'PA: Not creating a new room for %s' % patron.email
            return None

    def get_mxid_from_patron(self, patron, create_room=True):
        """Check in the patron's room to see if they've joined."""
        room = self.get_or_create_room(patron, create_room=create_room)
        if room is not None:
            invite_worked = False
            for event in Matrix.stream_messages(self.get_client(), room.room_id):
                if (event['type'] == 'm.room.member'
                        and event['sender'] != self.get_client().user_id):
                    room.leave()
                    return event['sender']
                if (event['type'] == 'm.room.third_party_invite'
                        or ('membership' in event and event['membership'] == 'invite')):
                    invite_worked = True
            if not invite_worked:
                print 'We didn\'t actually invite %s, retrying' % patron.email
                print 'PA: Reinviting %s' % patron.email, Matrix.invite_threepid_user(self.get_client(),
                                                                                      room.room_id,
                                                                                      patron.email)
        return None
