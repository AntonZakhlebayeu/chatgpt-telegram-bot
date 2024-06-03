import logging

import g4f
from g4f.client import Client

from exceptions import EmptyContentResponseError, ProviderRequestError

logger = logging.getLogger(__name__)
logging.basicConfig(filename="gpt_model.log")
logging.getLogger().setLevel(logging.INFO)


class GPTModelBase(type):
    """The base for implementing signleton GPT client implmented using metaclass"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GPTModel(metaclass=GPTModelBase):
    """The implementation of singleton GPT client"""

    def __init__(self):
        """initialize client with specific GPT provider
        this one works fine in tested contexts"""
        self.__client_gpt4 = Client()
        logger.info("GPT model initialized")

    def ask_gpt4(self, prompt: str, user_messages: list = None) -> str:
        """Method for communicating with ChatGPT version 4"""
        try:
            logger.info("sending request to GPT 4 provider")
            if user_messages:
                user_messages.append({"role": "user", "content": prompt})
                response = self.__client_gpt4.chat.completions.create(
                    model=g4f.models.default,
                    messages=user_messages,
                )
            else:
                response = self.__client_gpt4.chat.completions.create(
                    model=g4f.models.default,
                    messages=[{"role": "user", "content": prompt}],
                )
            logger.info("response from GPT 4 provider recieved")

            response_content = response.choices[0].message.content

            if response_content:
                logger.info("Response from GPT 4 provider returned to the user")
                return response_content
            else:
                logger.error("there is no message content from GPT 4 provider")
                raise EmptyContentResponseError(
                    "There is no response from ChatGPT, try to send the message again."
                )
        except Exception as exc:
            logger.error(
                f"There is an error with sending request to GPT 4 provider {repr(exc)}"
            )
            raise ProviderRequestError(
                f"There is an error with sending request to provider {repr(exc)}"
            )
