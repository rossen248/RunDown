import os
import time

from dotenv import load_dotenv, set_key, find_dotenv
from stravalib import Client, exc

load_dotenv()
dotenv_path = find_dotenv()


def force_reauth():
    """
    Clears stored token values and forces a reauthorization.
    """
    keys = ['STRAVA_ACCESS_TOKEN', 'STRAVA_REFRESH_TOKEN', 'STRAVA_TOKEN_EXPIRES']
    for key in keys:
        os.environ.pop(key, None)
        set_key(dotenv_path, key, "")
    print("Cleared stored tokens. Please reauthorize with correct scopes.")
    client = Client()
    auth_url = client.authorization_url(
        client_id=os.getenv('STRAVA_CLIENT_ID'),
        redirect_uri='http://localhost:5000/authorized',
        scope=['activity:read_all']
    )
    print(f"Authorize here: {auth_url}")
    code = input("Enter code from redirect URL: ").strip()
    token_response = client.exchange_code_for_token(
        client_id=os.getenv('STRAVA_CLIENT_ID'),
        client_secret=os.getenv('STRAVA_CLIENT_SECRET'),
        code=code
    )
    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']
    if 'expires_at' in token_response:
        client.token_expires = token_response['expires_at']
        set_key(dotenv_path, 'STRAVA_TOKEN_EXPIRES', str(client.token_expires))
        os.environ['STRAVA_TOKEN_EXPIRES'] = str(client.token_expires)
    os.environ['STRAVA_ACCESS_TOKEN'] = access_token
    os.environ['STRAVA_REFRESH_TOKEN'] = refresh_token
    set_key(dotenv_path, 'STRAVA_ACCESS_TOKEN', access_token)
    set_key(dotenv_path, 'STRAVA_REFRESH_TOKEN', refresh_token)
    client.access_token = access_token
    client.refresh_token = refresh_token
    return client


def authenticate_strava():
    client = Client()

    # Load tokens and token expiration if they exist
    access_token = os.getenv('STRAVA_ACCESS_TOKEN')
    refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
    token_expires_str = os.getenv('STRAVA_TOKEN_EXPIRES')
    if token_expires_str:
        try:
            client.token_expires = float(token_expires_str)
        except ValueError:
            client.token_expires = None

    # Initial authentication if no token exists
    if not access_token:
        print("No existing token found. Starting OAuth flow...")
        auth_url = client.authorization_url(
            client_id=os.getenv('STRAVA_CLIENT_ID'),
            redirect_uri='http://localhost:5000/authorized',
            scope=['activity:read_all']
        )
        print(f"Authorize here: {auth_url}")
        code = input("Enter code from redirect URL: ").strip()
        token_response = client.exchange_code_for_token(
            client_id=os.getenv('STRAVA_CLIENT_ID'),
            client_secret=os.getenv('STRAVA_CLIENT_SECRET'),
            code=code
        )
        access_token = token_response['access_token']
        refresh_token = token_response['refresh_token']
        if 'expires_at' in token_response:
            client.token_expires = token_response['expires_at']
            set_key(dotenv_path, 'STRAVA_TOKEN_EXPIRES', str(client.token_expires))
            os.environ['STRAVA_TOKEN_EXPIRES'] = str(client.token_expires)
        os.environ['STRAVA_ACCESS_TOKEN'] = access_token
        os.environ['STRAVA_REFRESH_TOKEN'] = refresh_token
        set_key(dotenv_path, 'STRAVA_ACCESS_TOKEN', access_token)
        set_key(dotenv_path, 'STRAVA_REFRESH_TOKEN', refresh_token)

    # Set tokens in client
    client.access_token = access_token
    client.refresh_token = refresh_token

    # Check token expiration based on stored timestamp
    if client.token_expires and time.time() > client.token_expires:
        print("Token expired based on timestamp. Refreshing...")
        refresh_response = client.refresh_access_token(
            client_id=os.getenv('STRAVA_CLIENT_ID'),
            client_secret=os.getenv('STRAVA_CLIENT_SECRET'),
            refresh_token=refresh_token
        )
        access_token = refresh_response['access_token']
        refresh_token = refresh_response['refresh_token']
        client.access_token = access_token
        if 'expires_at' in refresh_response:
            client.token_expires = refresh_response['expires_at']
            set_key(dotenv_path, 'STRAVA_TOKEN_EXPIRES', str(client.token_expires))
            os.environ['STRAVA_TOKEN_EXPIRES'] = str(client.token_expires)
        os.environ['STRAVA_ACCESS_TOKEN'] = access_token
        os.environ['STRAVA_REFRESH_TOKEN'] = refresh_token
        set_key(dotenv_path, 'STRAVA_ACCESS_TOKEN', access_token)
        set_key(dotenv_path, 'STRAVA_REFRESH_TOKEN', refresh_token)

    # Test token validity by fetching the athlete.
    try:
        client.get_athlete()
    except exc.AccessUnauthorized as e:
        error_details = e.response
        # Check if the error is related to missing activity read permission
        if isinstance(error_details, list) and any(
                item.get('field') == 'activity:read_permission' for item in error_details
        ):
            print("Token missing required permissions. Forcing reauthorization...")
            client = force_reauth()
        else:
            print("Access token invalid during API call. Refreshing token...")
            refresh_response = client.refresh_access_token(
                client_id=os.getenv('STRAVA_CLIENT_ID'),
                client_secret=os.getenv('STRAVA_CLIENT_SECRET'),
                refresh_token=refresh_token
            )
            access_token = refresh_response['access_token']
            refresh_token = refresh_response['refresh_token']
            client.access_token = access_token
            if 'expires_at' in refresh_response:
                client.token_expires = refresh_response['expires_at']
                set_key(dotenv_path, 'STRAVA_TOKEN_EXPIRES', str(client.token_expires))
                os.environ['STRAVA_TOKEN_EXPIRES'] = str(client.token_expires)
            os.environ['STRAVA_ACCESS_TOKEN'] = access_token
            os.environ['STRAVA_REFRESH_TOKEN'] = refresh_token
            set_key(dotenv_path, 'STRAVA_ACCESS_TOKEN', access_token)
            set_key(dotenv_path, 'STRAVA_REFRESH_TOKEN', refresh_token)
            # Optionally, retry the test API call
            try:
                client.get_athlete()
            except exc.AccessUnauthorized as e:
                print("Token refresh failed. Exiting.")
                raise e

    return client
