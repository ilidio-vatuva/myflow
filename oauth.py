
import os

from google_auth_oauthlib.flow import Flow

def generate_oauth_url(telegram_user_id):
    flow = get_oauth_flow()
    auth_url, _ = flow.authorization_url(
        prompt='consent',
        state=str(telegram_user_id),
        access_type='offline',
        include_granted_scopes='true'
    )
    return auth_url

def get_oauth_flow():
    webhook_url = os.getenv('WEBHOOK_URL')
    return Flow.from_client_secrets_file(
        'web_credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar.events'],
        redirect_uri=f'{webhook_url}/oauth/callback'
    )