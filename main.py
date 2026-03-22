from agent import execute_task 
from calendar_manager import get_events, create_event

def process_task(token, metadata):
    
    events = get_events(token)
    data = execute_task(metadata, events)
    create_event(token, title=data["calendar_event"]["title"], description=data["calendar_event"]["description"], 
                        start_time=data["calendar_event"]["suggested_start_time"], end_time=data["calendar_event"]["suggested_end_time"])
    return data

