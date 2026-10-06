import ollama

from personality import SYSTEM_PROMPT
from memory import save_message, get_recent_messages


MODEL = "llama3.2:3b"


def ask_hipolite(message):

    save_message("user", message)

    history = get_recent_messages(10)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    for role, content in history:
        messages.append({
            "role": role,
            "content": content
        })

    response = ollama.chat(
    model=MODEL,
    messages=messages,
    options={
        "temperature": 0.8,
        "num_predict": 150
    }
    )

    answer = response["message"]["content"]

    save_message("assistant", answer)

    return answer