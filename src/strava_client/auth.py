from stravalib import Client
from dotenv import load_dotenv
import os

load_dotenv()


def authenticate_strava():
    client = Client()

    # First-time authentication
    if not os.getenv('STRAVA_ACCESS_TOKEN'):
        auth_url = client.authorization_url(
            client_id=os.getenv('STRAVA_CLIENT_ID'),
            redirect_uri='http://localhost:5000/authorized',
            scope=['activity:read_all']
        )
        print(f"Authorize here: {auth_url}")
        code = input("Enter code from redirect URL: ")
        token = client.exchange_code_for_token(
            client_id=os.getenv('STRAVA_CLIENT_ID'),
            client_secret=os.getenv('STRAVA_CLIENT_SECRET'),
            code=code
        )
        os.environ['STRAVA_ACCESS_TOKEN'] = token['access_token']
        os.environ['STRAVA_REFRESH_TOKEN'] = token['refresh_token']

    client.access_token = os.getenv('STRAVA_ACCESS_TOKEN')

    # Auto-refresh token
    if client.is_token_expired():
        new_token = client.refresh_access_token(
            client_id=os.getenv('STRAVA_CLIENT_ID'),
            client_secret=os.getenv('STRAVA_CLIENT_SECRET'),
            refresh_token=os.getenv('STRAVA_REFRESH_TOKEN')
        )
        os.environ['STRAVA_ACCESS_TOKEN'] = new_token['access_token']
        client.access_token = new_token['access_token']

    return client