from agent import execute_task 
from calendar_manager import get_events, create_event, get_credentials

def process_task(task):
    gcreds = get_credentials()
    events = get_events(gcreds)
    data = execute_task(task, events)
    return create_event(creds=gcreds, title=data["calendar_event"]["title"], description=data["calendar_event"]["description"], 
                        start_time=data["calendar_event"]["suggested_start_time"], end_time=data["calendar_event"]["suggested_end_time"])

if __name__ == "__main__":
    event_details = process_task("Call the dentist")
    print(event_details)
    # send event_details to telegram