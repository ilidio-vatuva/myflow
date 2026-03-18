import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_credentials():
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
    
    creds = None
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)

      # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())
    return creds

def get_events(creds):
    try:
        service = get_service(creds)

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

        # Prints the start and name of the next 10 events
        for event in events:
          start = event["start"].get("dateTime", event["start"].get("date"))
        return events

    except HttpError as error:
        print(f"An error occurred: {error}")


def create_event(creds, title, description, start_time, end_time):
  event = {
    "summary": title,
    "description": description,
    "start": {"dateTime": start_time, "timeZone": "Europe/Madrid"},
    "end": {"dateTime": end_time, "timeZone": "Europe/Madrid"},
  }
  try:
      service = get_service(creds)
      event = service.events().insert(calendarId='primary', body=event).execute()
      return event
  except HttpError as error:
      print(f"An error occurred: {error}")

def get_service(creds):
    return build("calendar", "v3", credentials=creds)

if __name__ == "__main__":
    creds = get_credentials()
    events = get_events(creds)
    
    # Test creating an event
    create_event(
        creds=creds,
        title="Test - Call the dentist",
        description="Schedule routine checkup",
        start_time="2026-03-20T09:00:00",
        end_time="2026-03-20T09:15:00"
    )
    print("Event created!")