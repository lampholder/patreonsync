import sys
import traceback
from matrix_client.errors import MatrixRequestError

class Matrix(object):

    @staticmethod
    def stream_messages(client, internal_room_id):
        """Stream all the events in a room, backwards, from most recent to beginning of time."""
        end = None
        while True:
            batch = client.api.get_room_messages(internal_room_id, end, 'b', 10)
            end = batch['end']
            if len(batch['chunk']) == 0:
                break
            for event in batch['chunk']:
                yield event

    @staticmethod
    def invite_threepid_user(client, room_id, third_party_id):
        """Perform POST /room/$room_id/invite
        Args:
        room_id(str): The room ID
        third_party_id(str): The third party ID
        """
        body = {
            'id_server': 'vector.im',
            'medium': 'email',
            'address': third_party_id
        }
        try:
            #Matrix._send(client.api, 'POST', '/rooms/' + room_id + '/invite', body)
            client.api._send('POST', '/rooms/' + room_id + '/invite', body)
            return True
        except MatrixRequestError:
            sys.stderr.write(traceback.format_exc())
            return False
