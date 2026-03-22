from agent import execute_task 
from calendar_manager import get_events, create_event

def process_task(token, metadata):
    
    events = get_events(token)
    data = execute_task(metadata, events)
    event_type  = data["calendar_event"]["event_type"]
    print(f"Event type: {event_type}")
    print(f"Is reminder: {event_type == 'reminder'}")
    print(f"Will create event: {event_type != 'background'}")
    if event_type != "background":
        create_event(token, title=data["calendar_event"]["title"], description=data["calendar_event"]["description"], 
                        start_time=data["calendar_event"]["suggested_start_time"], end_time=data["calendar_event"]["suggested_end_time"], 
                        transparent=event_type == "reminder")
    return data

