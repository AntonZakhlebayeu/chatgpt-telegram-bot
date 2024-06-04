from telegram import InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from database_repo_telegram.client import db_client
from gpt_model import GPTVersion


GPT_VERSIONS = {
    GPTVersion.GPT_35_TURBO: "3.5",
    GPTVersion.GPT_4o: "4o",
    GPTVersion.GPT_4: "4",
}


def get_time_gpt_availability(user_id: int, version: GPTVersion) -> str:
    return f"""ChatGPT {GPT_VERSIONS[version]} currently unavailable, because you were reached out your limit.
You are switched to standard ChatGPT 3.5. ChatGPT {GPT_VERSIONS[version]} will be available at {db_client.get_availability_to_use_version(user_id, version)} at UTC."""


def get_gpt_version(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> GPTVersion:
    version = (
        context.user_data["gpt_version"]
        if context.user_data["gpt_version"]
        else GPTVersion.GPT_35_TURBO
    )
    if version == GPTVersion.GPT_35_TURBO:
        return version
    else:
        return (
            version
            if db_client.can_send_message(user_id, version)
            else GPTVersion.GPT_35_TURBO
        )


def chat_with_gpt_text(gpt_version: GPTVersion) -> str:
    return f"""Send your message to ChatGPT {GPT_VERSIONS[gpt_version]}. You can chatting with ChatGPT until you want it.
If you want to clear your conversation just click the button \"Clear conversation\". After it you can start your conversation for the beginning."""


def generate_keyboard_buttons(
    options: list, callback_data: list = None, urls: list = None
) -> list:
    if not callback_data:
        callback_data = [None] * len(options)

    if not urls:
        urls = [None] * len(options)

    if len(options) != len(callback_data) or len(options) != len(urls):
        raise ValueError(
            "Length of options should be equal to the length of callback_data and urls."
        )

    button_list = []

    for option, cb_data, url in zip(options, callback_data, urls):
        if cb_data and url:
            raise ValueError(
                "Each option should have either callback_data or a URL, not both."
            )

        if url:
            button = [InlineKeyboardButton(text=option, url=url)]
        else:
            button = [InlineKeyboardButton(text=option, callback_data=str(cb_data))]

        button_list.append(button)

    return button_list


def generate_column_oriented_buttons(
    options: list, callback_data: list = None, urls: list = None, columns: int = 2
) -> list:
    if not callback_data:
        callback_data = [None] * len(options)

    if not urls:
        urls = [None] * len(options)

    if len(options) != len(callback_data) or len(options) != len(urls):
        raise ValueError(
            "Length of options should be equal to the length of callback_data and urls."
        )

    button_list = []

    for option, cb_data, url in zip(options, callback_data, urls):
        if cb_data and url:
            raise ValueError(
                "Each option should have either callback_data or a URL, not both."
            )

        if url:
            button = InlineKeyboardButton(text=option, url=url)
        else:
            button = InlineKeyboardButton(text=option, callback_data=str(cb_data))

        button_list.append(button)

    return [button_list[n : n + columns] for n in range(0, len(button_list), columns)]
