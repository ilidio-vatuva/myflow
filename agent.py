from importlib import metadata

import anthropic
import json
import os

from dotenv import load_dotenv

load_dotenv()

def execute_task(metadata, events):

    system_prompt = os.getenv('SYSTEM_PROMPT')
    if not system_prompt:
        with open("knowledge/system_prompt.md", "r") as f:
            system_prompt = f.read()

    messages = [
        {
          "role": "user",
           "content": f"""Here are all task details: {metadata} And events: {events}""",
        }
    ]

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=1024, messages=messages, system=system_prompt
    )
    return json.loads(response.content[0].text)
