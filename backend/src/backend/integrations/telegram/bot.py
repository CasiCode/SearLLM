import logging
import os

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
API_KEY = os.getenv("SEARXTG_API_KEY")


# *Не ебу, как работает лоигрование, спизжено
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
api_url = f"{api_config.api.host}:{str(api_config.api.port)}"

api_client = APIClient(base_url=api_url, api_key=API_KEY)

bot_config = get_config("integrations/telegram/config.yml")


# *So far in Russian
async def searx_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    session_id = update.update_id

    # Update.message.text includes the command itself (/searx@SearXTG_bot or /searx)
    message = message.replace(
        f"/{bot_config.bot.search_command}@{bot_config.bot.bot_tag}", ""
    )
    message = message.replace(f"/{bot_config.bot.search_command}", "")
    # If there are only spaces after the command, they are not passed.
    message = message.strip()
    if len(message) == 0:
        await update.message.reply_text("Вы не ввели запрос")
        return

    query = {
        "session_id": update.update_id,
        "message": message,
        "user_id": update.effective_user.id,
    }

    response_json = await api_client.post(f"{api_url}/dev", data=query)
    try:
        response = OutputMessage.model_validate_json(response_json)
        if session_id == response.session_id:
            await update.message.reply_text(
                f"На запрос {message} В интернете найдено ЭТО: {response.message}"
            )
        else:
            await update.message.reply_text(
                f"На запрос {message} Произошла ошибка"
            )  # TODO: Change error handling
    except ValidationError as e:
        logger.warning(msg=f"Error validating the API response: {e}", stacklevel=3)
        update.message.reply_text("При обработке запроса произошла ошибка.")


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
