import anthropic
import json
import os
import requests

from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

def get_system_prompt():
    system_prompt = os.getenv('SYSTEM_PROMPT')
    if system_prompt:
        return system_prompt
    
    prompt_url = os.getenv('SYSTEM_PROMPT_URL')
    if prompt_url:
        response = requests.get(prompt_url)
        return response.text
    
    with open("knowledge/system_prompt.md", "r") as f:
        return f.read()

def execute_task(metadata, events):

    system_prompt = get_system_prompt()

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
