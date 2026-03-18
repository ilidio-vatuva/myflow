import anthropic
import json

from dotenv import load_dotenv

load_dotenv()

def execute_task(task, events):
    with open("knowledge/goals.md", "r") as f:
        goals = f.read()

    with open("knowledge/system_prompt.md", "r") as f:
        system_prompt = f.read()

    messages = [
        {
          "role": "user",
           "content": f"""Here are my goals and projects: {goals} New task: {task} And events: {events}""",
        }
    ]

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=1024, messages=messages, system=system_prompt
    )
    return json.loads(response.content[0].text)
