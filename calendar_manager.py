import datetime
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

def get_service(token):
    creds = Credentials.from_authorized_user_info(json.loads(token))
    return build("calendar", "v3", credentials=creds)

