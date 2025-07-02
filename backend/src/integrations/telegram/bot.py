import logging
from uuid import uuid4

import requests
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
    CallbackQueryHandler,
)

from backend.src.api.structs import OutputMessage
from backend.src.utils import get_config

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


async def process_query(query: str) -> OutputMessage:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    # TODO: Add query validation
    if not query:
        return

    query_json = {
        "session_id": "abc123",
        "message": query,
    }
    response_json = requests.post(f"{api_url}/dev", json=query_json)
    response = OutputMessage.model_validate_json(response_json)

    return response


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    if not query:
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Search",
            input_message_content=InputTextMessageContent("Click to search..."),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="🔍 Search:",
                            callback_data=f"search:{query}",
                        )
                    ]
                ]
            ),
        )
    ]

    await update.inline_query.answer(results, cache_time=0)


async def callback_handler(update, context):
    query = update.callback_query

    await query.answer()

    if query.data.startswith("search:"):
        actual_query = query.data.split("search:")[1]
        response = await process_query(actual_query)
        result_text = response.message

        await query.message.reply_text(result_text)


def main() -> None:
    """Run the bot."""
    application = (
        Application.builder().token("TOKEN").build()
    )  # TODO: Change the token and add to env

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(InlineQueryHandler(inline_query))
    application.add_handler(CallbackQueryHandler(callback_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
