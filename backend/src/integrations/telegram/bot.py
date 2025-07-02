import logging
import requests

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler

from backend.src.utils import get_config
from backend.src.api.structs import OutputMessage


api_config = get_config("../../api/config.yml")
api_url = f"{api_config.host}:{str(api_config.port)}"


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    if not query:
        return

    query_json = {
        "session_id": "abc123",
        "message": query,
    }
    response_json = requests.post(f"{api_url}/dev", json=query_json)
    response = OutputMessage.model_validate_json(response_json)

    await update.inline_query.answer(response.message)


def main() -> None:
    """Run the bot."""
    application = (
        Application.builder().token("TOKEN").build()
    )  # TODO: Change the token and add to env

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(InlineQueryHandler(inline_query))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
