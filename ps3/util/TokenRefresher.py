import yaml
import requests

def refresh_token(config_file):
    with open(config_file, 'r') as infile:
        config = yaml.load(infile)

        params = {
            'grant_type': 'refresh_token',
            'refresh_token': config['patreon']['creator_refresh_token'],
            'client_id': config['patreon']['client_id'],
            'client_secret': config['patreon']['client_secret']
        }

        response = requests.post('https://www.patreon.com/api/oauth2/token',
                                 params=params)

        if response.status_code != 200:
            import json
            print json.dumps(response.json(), indent=2)
            raise Exception('Invalid Patreon credentials; go to ' +
                            'https://www.patreon.com/portal/registration/register-clients ' +
                            'and sort it out!')

        response_body = response.json()

        config['patreon']['creator_access_token'] = response_body['access_token'].encode('ascii')
        config['patreon']['creator_refresh_token'] = response_body['refresh_token'].encode('ascii')

    with open(config_file, 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)
