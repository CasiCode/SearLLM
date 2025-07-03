from .handlers import (
    start,
    help_command,
    searx_command,
    chat_question,
)

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from backend.utils import get_config

from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")

# config_bot = get_config("../../config.yml")
# *config.yml is not used yet
search_command = "searx"


# *Не ебу, как работает лоигрование, спизжено
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler(search_command, searx_command))

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, chat_question
        )
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
