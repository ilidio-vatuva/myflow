from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    nickname: str
    telegram_id: str
    google_token: Optional[str] = None,
    language: Optional[str] = None

@dataclass
class Goal:
    id: int
    user_id: int
    name: str
    importance: int
    description: Optional[str] = None

@dataclass
class Project:
    id: int
    goal_id: int
    name: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    hours: Optional[int] = None
    frequency: Optional[str] = None

@dataclass
class Task:
    id: int
    project_id: int
    title: str
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    planned_duration: Optional[int] = None
    spent_time: Optional[int] = None
    calendar_event_id: Optional[str] = None

@dataclass
class Conversation:
    id: int
    user_id: int
    role: str
    message: str
    created_at: str