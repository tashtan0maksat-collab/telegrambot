import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts import SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)

_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)

_chats: dict[int, genai.ChatSession] = {}


def get_response(user_id: int, message: str) -> str:
    if user_id not in _chats:
        _chats[user_id] = _model.start_chat()

    try:
        response = _chats[user_id].send_message(message)
        return response.text
    except Exception:
        _chats.pop(user_id, None)
        try:
            _chats[user_id] = _model.start_chat()
            response = _chats[user_id].send_message(message)
            return response.text
        except Exception as e:
            return f"Кешіріңіз, қате орын алды. Кейінірек қайталап көріңіз.\n\nҚате: {e}"
