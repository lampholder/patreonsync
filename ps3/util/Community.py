import json
import requests

class Community(object):

    def __init__(self, id, homeserver='https://matrix.org'):
        self._id = id
        self._homeserver = homeserver

    def _api(self, method, url, access_token):
        url = self._homeserver + url
        params = {'access_token': access_token}
        headers = {'Content-Type': 'application/json'}

        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'PUT':
            data = json.dumps({})
            response = requests.put(url, params=params, headers=headers,
                                    data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.status_code, response.content)

    def invite(self, mxid, access_token):
        url = '/_matrix/client/r0/groups/%s/admin/users/invite/%s'
        return self._api('PUT', url % (self._id, mxid), access_token)

    def remove(self, mxid, access_token):
        url = '/_matrix/client/r0/groups/%s/admin/users/remove/%s'
        return self._api('PUT', url % (self._id, mxid), access_token)

    def invited_users(self, access_token):
        url = '/_matrix/client/r0/groups/%s/invited_users'
        response = self._api('GET', url % self._id, access_token)
        return [u['user_id'] for u in response['chunk']]

    def members(self, access_token):
        url = '/_matrix/client/r0/groups/%s/users'
        response = self._api('GET', url % self._id, access_token)
        return [u['user_id'] for u in response['chunk']]
