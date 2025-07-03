import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


from backend.api.structs import OutputMessage
from backend.utils import get_config
import requests

# config = get_config("backend/src/backend/api/config.yml")
# api_url = f"{config.host}:{str(config.port)}"


search_command = "searx"

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


# *So far in Russian
async def searx_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    session_id = update.update_id
    # Update.message.text includes the command itself
    # *message = message[len("/" + search_command) + 1 :]
    # *This option does not work in the group due to the format "/searx@SearXTG_bot".
    # *It would be possible to make two separate handlers and two functions. Shit?

    # *Telegram does not transmit spaces if there were no other characters in the message
    position_s = message.find(" ")
    if position_s == -1:
        await update.message.reply_text("Вы не ввели запрос")
        return

    message = message[position_s + 1 :]

    """
    query = {
        "session_id": update.update_id,
        "message": message,
    }

    response_json = requests.post(f"{api_url}/dev", json=query)
    response = OutputMessage.model_validate_json(response_json)
    """

    if session_id == session_id:  # *session_id == response.session_id
        await update.message.reply_text(f"На запрос {message} В интернете найдено ЭТО")
    else:
        await update.message.reply_text(f"На запрос {message} Произошла ошибка")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    # *The implementation will be the same as that of the searx_command
    await update.message.reply_text(f"На запрос {message} В интернете найдено ЭТО")


token = "8033838222:AAHwXHZgM5mEUfG-YVFzZ9I3za9kyfNrWyA"


def main() -> None:
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler(search_command, searx_command))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, echo)
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
