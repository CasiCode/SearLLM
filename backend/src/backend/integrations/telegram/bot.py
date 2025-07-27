import logging
import os
import asyncio
import uuid

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from pydantic import ValidationError

from backend.api.core.structs import OutputMessage
from backend.utils import get_config
from backend.api.client import APIClient


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


api_config = get_config("api/config.yml")
bot_config = get_config("integrations/telegram/config.yml")

api_url = f"{api_config.api.host}:{str(api_config.api.port)}"
api_client = APIClient(base_url=api_url)


async def searx_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    session_id = update.update_id

    # Update.message.text includes the command itself (/searx@SearLLM_bot or /searx)
    message = message.replace(f"/{bot_config.bot.search_command}", "")
    message = message.replace(f"@{bot_config.bot.bot_tag}", "")

    # If there are only spaces after the command, they are not passed.
    message = message.strip()
    if len(message) == 0:
        await update.message.reply_text(
            "You haven't queried anything"
        )  # TODO: Add localization
        return

    query = {
        "session_id": uuid.uuid4(),
        "message": message,
        "user_id": update.effective_user.id,
    }
    async with APIClient(base_url=api_url) as client:
        try:
            response_json = await asyncio.wait_for(
                client.post("queries/query", data=query), timeout=60
            )
        except asyncio.TimeoutError:
            update.message.reply_text(
                "Oops, sorry! Our server couldn't process your request in time."
            )
        if response_json is None:
            update.message.reply_text(
                "Oops, sorry! We encountered an error trying to process your request."
            )
        else:
            try:
                response = OutputMessage.model_validate_json(response_json)
                if session_id == response.session_id:
                    await update.message.reply_text(
                        text="{}\n\nSources:\n{}".format(
                            response.message, "\n".join(response.source_documents)
                        )
                    )
                else:
                    await update.message.reply_text(
                        "Oops, sorry! Our server couldn't catch the correct session for your request."
                    )  # TODO: Change error handling
            except ValidationError as e:
                logger.warning(
                    msg=f"Error validating the API response: {e}", stacklevel=3
                )
                update.message.reply_text(
                    "Oops, sorry! We encountered an error trying to process your request."
                )


async def chat_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    # *The implementation will be the same as that of the searx_command
    await update.message.reply_text(f"На запрос {message} В интернете найдено ЭТО")


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        CommandHandler(bot_config.bot.search_command, searx_command)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, chat_question
        )
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
