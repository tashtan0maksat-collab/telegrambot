import time
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts import SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)

_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)

_chats: dict[int, genai.ChatSession] = {}

MAX_RETRIES = 3


def get_response(user_id: int, message: str) -> str:
    if user_id not in _chats:
        _chats[user_id] = _model.start_chat()

    for attempt in range(MAX_RETRIES):
        try:
            response = _chats[user_id].send_message(message)
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                wait = 35 * (attempt + 1)
                time.sleep(wait)
                continue
            _chats.pop(user_id, None)
            _chats[user_id] = _model.start_chat()
            try:
                response = _chats[user_id].send_message(message)
                return response.text
            except Exception as e2:
                return f"Кешіріңіз, қате орын алды. Кейінірек қайталап көріңіз.\n\nҚате: {e2}"

    return "Кешіріңіз, қазір сұраулар көп. 1 минуттан кейін қайталап көріңіз. ⏳"
