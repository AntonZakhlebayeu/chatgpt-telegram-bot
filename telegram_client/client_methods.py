import logging

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database_repo_telegram.client import db_client
from exceptions import EmptyContentResponseError, ProviderRequestError
from gpt_model import GPTModel, GPTVersion
from telegram_client.constants import (ABOUT_PROJECT, ABOUT_PROJECT_TEXT,
                                       ASK_GPT, ASK_GPT_BUTTON_TEXT,
                                       ASK_GPT_TEXT, AWAITING_USER_MESSAGE,
                                       BACK_TO_MAIN_MENU,
                                       BACK_TO_MAIN_MENU_BUTTON_TEXT,
                                       BACK_TO_SELECTION,
                                       BACK_TO_SELECTION_BUTTON_TEXT,
                                       CHAT_GPT_BUTTON_TEXT,
                                       CLEAR_CONVERSATION,
                                       CONVERSATION_CLEARED_TEXT, GPT_4,
                                       GPT_4O, GPT_35, MAIN_MENU,
                                       MAIN_MENU_BUTTON_TEXT, MAIN_MENU_TEXT,
                                       SELECTING_ACTION, SELECTING_VERSION,
                                       WELCOME_MESSAGE,
                                       WELCOME_MESSAGE_BUTTON_TEXT,
                                       WELCOME_MESSAGE_TEXT)
from telegram_client.utils import (chat_with_gpt_text,
                                   generate_keyboard_buttons, get_gpt_version,
                                   get_time_gpt_availability)

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


async def handle_text_reply_chatgpt(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    gpt_version = get_gpt_version(update.effective_chat.id, context)
    if gpt_version != context.user_data["gpt_version"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_time_gpt_availability(
                update.effective_chat.id, context.user_data["gpt_version"]
            ),
        )

    user_input = update.message.text
    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            CHAT_GPT_BUTTON_TEXT,
            callback_data=[CLEAR_CONVERSATION, BACK_TO_SELECTION],
        )
    )

    gpt_model = GPTModel()
    try:
        user_messages = db_client.get_user_messages(update.effective_chat.id)
        if len(user_messages) == 0:
            response_from_gpt = gpt_model.ask_gpt(user_input, version=gpt_version)
        else:
            response_from_gpt = gpt_model.ask_gpt(
                user_input, user_messages, gpt_version
            )
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

    db_client.add_message(update.effective_chat.id, "user", user_input, gpt_version)
    db_client.add_message(
        update.effective_chat.id, "assistant", response_from_gpt, gpt_version
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_from_gpt,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )

    return AWAITING_USER_MESSAGE


async def chat_gpt_4(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["gpt_version"] = GPTVersion.GPT_4

    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            CHAT_GPT_BUTTON_TEXT,
            callback_data=[CLEAR_CONVERSATION, BACK_TO_SELECTION],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=chat_with_gpt_text(GPTVersion.GPT_4),
        reply_markup=keyboard,
    )

    return AWAITING_USER_MESSAGE


async def chat_gpt_4o(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("entered 4o")
    context.user_data["gpt_version"] = GPTVersion.GPT_4o

    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            CHAT_GPT_BUTTON_TEXT,
            callback_data=[CLEAR_CONVERSATION, BACK_TO_SELECTION],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=chat_with_gpt_text(GPTVersion.GPT_4o),
        reply_markup=keyboard,
    )

    return AWAITING_USER_MESSAGE


async def chat_gpt_35(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["gpt_version"] = GPTVersion.GPT_35_TURBO

    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            CHAT_GPT_BUTTON_TEXT,
            callback_data=[CLEAR_CONVERSATION, BACK_TO_SELECTION],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=chat_with_gpt_text(GPTVersion.GPT_35_TURBO),
        reply_markup=keyboard,
    )

    return AWAITING_USER_MESSAGE


async def ask_gpt_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["gpt_version"] = None

    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            ASK_GPT_BUTTON_TEXT,
            callback_data=[GPT_35, GPT_4O, GPT_4, BACK_TO_MAIN_MENU],
        )
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ASK_GPT_TEXT,
        reply_markup=keyboard,
    )

    return BACK_TO_SELECTION


async def ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["gpt_version"] = None

    keyboard = InlineKeyboardMarkup(
        generate_keyboard_buttons(
            ASK_GPT_BUTTON_TEXT,
            callback_data=[GPT_35, GPT_4O, GPT_4, BACK_TO_MAIN_MENU],
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
