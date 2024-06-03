import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          MessageHandler, PicklePersistence, filters)

from telegram_client.client_methods import (about_the_project, ask_gpt,
                                            ask_gpt_nested, chat_gpt_4,
                                            clear_conversation_handler,
                                            handle_text_reply_chatgpt_4,
                                            main_menu, main_menu_nested, start)
from telegram_client.config import config
from telegram_client.constants import (ABOUT_PROJECT, ASK_GPT,
                                       AWAITING_USER_MESSAGE,
                                       BACK_TO_MAIN_MENU, BACK_TO_SELECTION,
                                       CLEAR_CONVERSATION, GPT_4, MAIN_MENU,
                                       SELECTING_ACTION, SELECTING_VERSION,
                                       WELCOME_MESSAGE)
from telegram_client.conversation_handler_factory import \
    ConversationHandlerFactory


class TelegramClient:
    """This is a telegram client for communicating with ChatGPT using the telegram client"""

    def __init__(self) -> None:
        persistence = PicklePersistence(
            filepath="chatgpt_own_bot.pkl", update_interval=1
        )
        self.__application = (
            Application.builder()
            .token(config.get("TELEGRAM_TOKEN"))
            .read_timeout(30)
            .write_timeout(30)
            .persistence(persistence)
            .build()
        )
        self.__conversation_handler_factory = ConversationHandlerFactory(
            persistent=True
        )

    def __configure_telegram_client(self):
        """Configure telegram client using ConversationHandlerFactory"""
        chat_gpt_4_handler = self.__conversation_handler_factory.create(
            entry_points=[
                CallbackQueryHandler(chat_gpt_4, pattern=f"^{str(GPT_4)}$"),
            ],
            states={
                AWAITING_USER_MESSAGE: [
                    MessageHandler(filters.TEXT, handle_text_reply_chatgpt_4)
                ],
            },
            fallbacks=[
                CallbackQueryHandler(
                    ask_gpt_nested,
                    pattern=f"^{str(BACK_TO_SELECTION)}$",
                ),
                CallbackQueryHandler(
                    clear_conversation_handler,
                    pattern=f"^{str(CLEAR_CONVERSATION)}$",
                ),
            ],
            map_to_parent={BACK_TO_SELECTION: SELECTING_VERSION},
            name="chat_gpt_4_conv",
        )

        ask_gpt_handler = self.__conversation_handler_factory.create(
            entry_points=[
                CallbackQueryHandler(ask_gpt, pattern=f"^{str(ASK_GPT)}$"),
            ],
            states={
                SELECTING_VERSION: [
                    chat_gpt_4_handler,
                ],
            },
            fallbacks=[
                CallbackQueryHandler(
                    main_menu_nested,
                    pattern=f"^{str(BACK_TO_MAIN_MENU)}$",
                ),
                CallbackQueryHandler(ask_gpt, pattern=f"^{str(BACK_TO_SELECTION)}$"),
            ],
            map_to_parent={BACK_TO_MAIN_MENU: SELECTING_ACTION},
            name="ask_gpt_conv",
        )

        main_menu_handler = self.__conversation_handler_factory.create(
            entry_points=[
                CallbackQueryHandler(main_menu, pattern=f"^{str(MAIN_MENU)}$"),
            ],
            states={
                SELECTING_ACTION: [
                    ask_gpt_handler,
                ],
            },
            fallbacks=[
                CallbackQueryHandler(
                    main_menu,
                    pattern=f"^{str(BACK_TO_MAIN_MENU)}$",
                ),
                CallbackQueryHandler(
                    about_the_project, pattern=f"^{str(ABOUT_PROJECT)}$"
                ),
            ],
            name="main_menu_conv",
        )

        start_handler = self.__conversation_handler_factory.create(
            entry_points=[CommandHandler("start", start)],
            states={
                WELCOME_MESSAGE: [
                    main_menu_handler,
                ],
            },
            fallbacks=[],
            name="start_conv_handler",
        )

        self.__application.add_handler(start_handler)

    def run_telegram_client(self) -> None:
        """Start up the telegram client"""
        self.__configure_telegram_client()

        self.__application.run_polling(allowed_updates=Update.ALL_TYPES)
