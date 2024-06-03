import logging

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database_repo_telegram.client import db_client
from exceptions import EmptyContentResponseError, ProviderRequestError
from gpt_model import GPTModel
from telegram_client.constants import (ABOUT_PROJECT, ABOUT_PROJECT_TEXT,
                                       ASK_GPT, ASK_GPT_BUTTON_TEXT,
                                       ASK_GPT_TEXT, AWAITING_USER_MESSAGE,
                                       BACK_TO_MAIN_MENU,
                                       BACK_TO_MAIN_MENU_BUTTON_TEXT,
                                       BACK_TO_SELECTION,
                                       BACK_TO_SELECTION_BUTTON_TEXT,
                                       CHAT_GPT_4_BUTTON_TEXT, CHAT_GPT_4_TEXT,
                                       CLEAR_CONVERSATION,
                                       CONVERSATION_CLEARED_TEXT, GPT_4,
                                       MAIN_MENU, MAIN_MENU_BUTTON_TEXT,
                                       MAIN_MENU_TEXT, SELECTING_ACTION,
                                       SELECTING_VERSION, WELCOME_MESSAGE,
                                       WELCOME_MESSAGE_BUTTON_TEXT,
                                       WELCOME_MESSAGE_TEXT)
from telegram_client.utils import generate_keyboard_buttons

logger = logging.getLogger(__name__)
logging.basicConfig(filename="gpt_model.log")
logging.getLogger().setLevel(logging.INFO)


async def clear_conversation_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    db_client.delete_messages_by_user_id(update.effective_chat.id)

    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            BACK_TO_SELECTION_BUTTON_TEXT,
            callback_data=[BACK_TO_SELECTION],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=CONVERSATION_CLEARED_TEXT,
        reply_markup=keyboard,
    )

    return AWAITING_USER_MESSAGE


async def handle_text_reply_chatgpt_4(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_input = update.message.text
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            CHAT_GPT_4_BUTTON_TEXT,
            callback_data=[CLEAR_CONVERSATION, BACK_TO_SELECTION],
        )
    )

    gpt_model = GPTModel()
    try:
        user_messages = db_client.get_user_messages(update.effective_chat.id)
        if len(user_messages) == 0:
            response_from_gpt = gpt_model.ask_gpt4(user_input)
        else:
            response_from_gpt = gpt_model.ask_gpt4(user_input, user_messages)
    except EmptyContentResponseError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="There is an empty response from gpt provider, try to send again your message",
            reply_markup=keyboard,
        )

        return AWAITING_USER_MESSAGE
    except ProviderRequestError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="There is an issue with gpt provider, try to send again your message",
            reply_markup=keyboard,
        )

        return AWAITING_USER_MESSAGE

    db_client.add_message(update.effective_chat.id, "user", user_input)
    db_client.add_message(update.effective_chat.id, "assistant", response_from_gpt)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_from_gpt,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )

    return AWAITING_USER_MESSAGE


async def chat_gpt_4(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            CHAT_GPT_4_BUTTON_TEXT,
            callback_data=[CLEAR_CONVERSATION, BACK_TO_SELECTION],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=CHAT_GPT_4_TEXT,
        reply_markup=keyboard,
    )

    return AWAITING_USER_MESSAGE


async def ask_gpt_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            ASK_GPT_BUTTON_TEXT,
            callback_data=[GPT_4, BACK_TO_MAIN_MENU],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ASK_GPT_TEXT,
        reply_markup=keyboard,
    )

    return BACK_TO_SELECTION


async def ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            ASK_GPT_BUTTON_TEXT,
            callback_data=[GPT_4, BACK_TO_MAIN_MENU],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ASK_GPT_TEXT,
        reply_markup=keyboard,
    )

    return SELECTING_VERSION


async def about_the_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            BACK_TO_MAIN_MENU_BUTTON_TEXT,
            callback_data=[BACK_TO_MAIN_MENU],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ABOUT_PROJECT_TEXT,
        reply_markup=keyboard,
    )


async def main_menu_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            MAIN_MENU_BUTTON_TEXT,
            callback_data=[ASK_GPT, ABOUT_PROJECT],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=MAIN_MENU_TEXT,
        reply_markup=keyboard,
    )

    return BACK_TO_MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            MAIN_MENU_BUTTON_TEXT,
            callback_data=[ASK_GPT, ABOUT_PROJECT],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=MAIN_MENU_TEXT,
        reply_markup=keyboard,
    )

    return SELECTING_ACTION


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            WELCOME_MESSAGE_BUTTON_TEXT,
            callback_data=[MAIN_MENU],
        )
    )

    logger.info(
        f"Just started user {update.effective_user.id}, with username {update.message.from_user.username}"
    )
    db_client.add_user(update.effective_user.id)

    await update.message.reply_text(
        text=WELCOME_MESSAGE_TEXT,
        reply_markup=keyboard,
    )

    return WELCOME_MESSAGE
