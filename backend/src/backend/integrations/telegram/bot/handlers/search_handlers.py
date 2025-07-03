# import requests

from telegram import Update
from telegram.ext import ContextTypes

# from backend.api.structs import OutputMessage
from backend.utils import get_config


api_config = get_config("api/config.yml")
api_url = f"{api_config.host}:{str(api_config.port)}"

bot_config = get_config("integrations/telegram/config.yml")


# *So far in Russian
async def searx_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    session_id = update.update_id

    # Update.message.text includes the command itself (/searx@SearXTG_bot or /searx)
    message = message.replace(f"/{bot_config.search_command}@{bot_config.bot_tag}", "")
    message = message.replace(f"/{bot_config.search_command}", "")
    # If there are only spaces after the command, they are not passed.
    if len(message) == 0:
        await update.message.reply_text("Вы не ввели запрос")
        return
    message = message.lstrip()

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


async def chat_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    # *The implementation will be the same as that of the searx_command
    await update.message.reply_text(f"На запрос {message} В интернете найдено ЭТО")
