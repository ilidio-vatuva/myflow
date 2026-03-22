
import os

from google_auth_oauthlib.flow import Flow

_flows = {}

def generate_oauth_url(telegram_user_id):
    flow = get_oauth_flow()
    auth_url, _ = flow.authorization_url(
        prompt='consent',
        state=str(telegram_user_id),
        access_type='offline'
    )
    _flows[str(telegram_user_id)] = flow
    return auth_url

def get_oauth_flow():
    webhook_url = os.getenv('WEBHOOK_URL')
    return Flow.from_client_secrets_file(
        'web_credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar.events'],
        redirect_uri=f'{webhook_url}/oauth/callback'
    )

def fetch_token(telegram_user_id, code):
    flow = _flows.get(str(telegram_user_id))
    if not flow:
        raise Exception("No flow found for user")
    flow.fetch_token(code=code)
    _flows.pop(str(telegram_user_id))  # cleanup
    return flow.credentials