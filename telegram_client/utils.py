from telegram import InlineKeyboardButton


def generate_keyboard_buttons(options, callback_data=None, urls=None):
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
    options, callback_data=None, urls=None, columns: int = 2
):
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
