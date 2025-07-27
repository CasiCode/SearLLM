from telegram import Update
from telegram.ext import ContextTypes

from backend.utils import get_config

from backend.api.client import APIClient
from backend.api.core.structs import OutputMessage


api_config = get_config("api/config.yml")
API_URL = f"{api_config.api.host}:{str(api_config.api.port)}"

bot_config = get_config("integrations/telegram/config.yml")


# *So far in Russian
async def searx_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    session_id = update.update_id

    # Update.message.text includes the command itself (/searx@SearLLM_bot or /searx)
    message = message.replace(
        f"/{bot_config.bot.search_command}@{bot_config.bot.bot_tag}", ""
    )
    message = message.replace(f"/{bot_config.bot.search_command}", "")
    # If there are only spaces after the command, they are not passed.
    if len(message) == 0:
        await update.message.reply_text("Вы не ввели запрос")
        return
    message = message.lstrip()

    query = {
        "session_id": update.update_id,
        "user_ID": update.effective_user.id,
        "message": message,
    }

    async with APIClient(base_url=API_URL) as client:
        response_json = await client.post("queries/dev", data=query)
        response = OutputMessage(**response_json)
        if session_id == response.session_id:
            await update.message.reply_text(
                f"На запрос {message} В интернете найдено ЭТО"
            )
        else:
            await update.message.reply_text(f"На запрос {message} Произошла ошибка")


async def chat_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    # *The implementation will be the same as that of the searx_command
    await update.message.reply_text(f"На запрос {message} В интернете найдено ЭТО")
