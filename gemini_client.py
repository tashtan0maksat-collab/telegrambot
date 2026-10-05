import time
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

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
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            logger.warning("Rate limit hit for user %s, retrying in 10s", user_id)
            time.sleep(10)
            try:
                response = _chats[user_id].send_message(message)
                return response.text
            except Exception:
                return "Кешіріңіз, қазір сұраулар көп. Бір минуттан кейін қайталап көріңіз ⏳"

        logger.error("Gemini error for user %s: %s", user_id, e)
        _chats.pop(user_id, None)
        _chats[user_id] = _model.start_chat()
        try:
            response = _chats[user_id].send_message(message)
            return response.text
        except Exception:
            return "Кешіріңіз, техникалық ақау орын алды. Кейінірек қайталап көріңіз 🔧"
