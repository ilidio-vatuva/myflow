from enum import Enum


user_sessions = {}

class SessionState(Enum):
    # New user flow
    WAITING_FOR_NICKNAME = "waiting_for_nickname"
    WAITING_FOR_PREFERRED_LANGUAGE = "waiting_for_preferred_language"

    # New task flow
    WAITING_FOR_TASK = "waiting_for_task"
    WAITING_FOR_PROJECT = "waiting_for_project"
    WAITING_FOR_DEADLINE = "waiting_for_deadline"
    
    # New project flow
    WAITING_FOR_PROJECT_GOAL = "waiting_for_project_goal"
    WAITING_FOR_PROJECT_NAME = "waiting_for_project_name"
    WAITING_FOR_PROJECT_DESC = "waiting_for_project_desc"
    WAITING_FOR_PROJECT_HOURS = "waiting_for_project_hours"
    WAITING_FOR_PROJECT_FREQUENCY = "waiting_for_project_frequency"
    WAITING_FOR_PROJECT_DUE_DATE = "waiting_for_project_due_date"
    
    # New goal flow
    WAITING_FOR_GOAL_NAME = "waiting_for_goal_name"
    WAITING_FOR_GOAL_DESC = "waiting_for_goal_desc"
    WAITING_FOR_GOAL_IMPORTANCE = "waiting_for_goal_importance"
    WAITING_FOR_RESCHEDULE_REASON = "waiting_for_reschedule_reason"
    
    # Management flows
    EDITING_GOAL_NAME = "editing_goal_name"
    EDITING_GOAL_DESC = "editing_goal_desc"
    EDITING_GOAL_IMPORTANCE = "editing_goal_importance"
    
    EDITING_PROJECT_NAME = "editing_project_name"
    EDITING_PROJECT_DESC = "editing_project_desc"
    EDITING_PROJECT_HOURS = "editing_project_hours"
    EDITING_PROJECT_FREQUENCY = "editing_project_frequency"
    EDITING_PROJECT_DUE_DATE = "editing_project_due_date"
    EDITING_PROJECT = "editing_project"
    EDITING_TASK_TITLE = "editing_task_title"
    EDITING_NICKNAME = "editing_nickname"
    EDITING_PREFERRED_LANGUAGE = "editing_preferred_language"

def get_session(telegram_user_id):
    return user_sessions.get(telegram_user_id, {"state": SessionState.WAITING_FOR_TASK})

def update_session(telegram_user_id, data):
    if telegram_user_id not in user_sessions:
        user_sessions[telegram_user_id] = {}
    user_sessions[telegram_user_id].update(data)

def clear_session(telegram_user_id):
    user_sessions.pop(telegram_user_id, None)
