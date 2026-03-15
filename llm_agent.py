from groq import Groq
import os
import json
from dotenv import load_dotenv
from tools import TOOLS

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOL_DEFS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
]


def run_agent(messages, model):
    # Step 1: non-streaming call so tool call arguments arrive complete
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOL_DEFS,
        tool_choice="auto",
    )

    msg = response.choices[0].message
    augmented = list(messages)

    if msg.tool_calls:
        # Execute every requested tool and collect results
        augmented.append(msg)
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            result = TOOLS[name](**args)
            augmented.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

        # Step 2: stream the final answer that incorporates tool results
        stream = client.chat.completions.create(
            model=model,
            messages=augmented,
            stream=True,
        )
    else:
        # No tools needed — stream a direct response
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
