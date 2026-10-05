import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import TELEGRAM_BOT_TOKEN
from gemini_client import get_response

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "Сәлеметсіз бе! 👋\n\n"
    "Мен — стоматология клиникасының AI-ассистентімін 🦷\n\n"
    "Мен сізге көмектесе аламын:\n"
    "• Қызметтер мен бағалар туралы ақпарат\n"
    "• Жұмыс уақыты мен мекенжай\n"
    "• Тіс күтімі бойынша кеңестер\n"
    "• Дәрігерге жазылу\n\n"
    "Сұрағыңызды жазыңыз!"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Маған кез-келген стоматологияға қатысты сұрақ қоюға болады:\n\n"
        "• Бағалар қанша?\n"
        "• Жұмыс уақыты?\n"
        "• Тіс ауырса не істеу керек?\n"
        "• Қалай жазылуға болады?\n\n"
        "Жай ғана сұрағыңызды жазыңыз! 😊"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_message = update.message.text

    logger.info("User %s: %s", user_id, user_message)

    await update.message.chat.send_action("typing")

    reply = get_response(user_id, user_message)

    if len(reply) > 4096:
        for i in range(0, len(reply), 4096):
            await update.message.reply_text(reply[i : i + 4096])
    else:
        await update.message.reply_text(reply)


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
