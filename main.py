from agent import execute_task 
from calendar_manager import get_events, create_event

def process_task(token, metadata, conversation_history=None):
    
    events = get_events(token)
    data = execute_task(metadata, events, conversation_history=conversation_history)
    event_type  = data["calendar_event"]["event_type"]
    if event_type != "background":
        created_event = create_event(token, title=data["calendar_event"]["title"], description=data["calendar_event"]["description"], 
                        start_time=data["calendar_event"]["suggested_start_time"], end_time=data["calendar_event"]["suggested_end_time"], 
                        transparent=event_type == "reminder")
        data["calendar_event"]["id"] = created_event["id"]
    return data