import datetime
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_events(token):
    try:
        service = get_service(token)

        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        print("Getting the upcoming events for the next 30 days")
        time_max = (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=30)).isoformat()
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
          print("No upcoming events found.")
          return

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")
    except Exception as error:
        if "invalid_grant" in str(error):
            raise TokenExpiredError()
        raise

def get_today_events(token):
    try:
        service = get_service(token)
        madrid_tz = pytz.timezone('Europe/Madrid')
        now = datetime.datetime.now(madrid_tz)
        start_of_day = now.replace(hour=0, minute=0, second=0).isoformat()
        end_of_day = now.replace(hour=23, minute=59, second=59).isoformat()
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return events_result.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    
def create_event(token, title, description, start_time, end_time, transparent=False):
    event = {
      "summary": title,
      "description": description,
      "start": {"dateTime": start_time, "timeZone": "Europe/Madrid"},
      "end": {"dateTime": end_time, "timeZone": "Europe/Madrid"},
      "transparency": "transparent" if transparent else "opaque"
    }
    try:
      service = get_service(token)
      event = service.events().insert(calendarId='primary', body=event).execute()
      return event
    except HttpError as error:
        print(f"An error occurred: {error}")
    except Exception as error:
        if "invalid_grant" in str(error):
            raise TokenExpiredError()
        raise

def delete_event(token, event_id):
    try:
        service = get_service(token)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
    except HttpError as error:
        print(f"An error occurred: {error}")
    except Exception as error:
        if "invalid_grant" in str(error):
            raise TokenExpiredError()
        raise
    
def get_service(token):
    creds = Credentials.from_authorized_user_info(json.loads(token))
    return build("calendar", "v3", credentials=creds)


class TokenExpiredError(Exception):
    pass
