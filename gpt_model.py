import logging
from enum import StrEnum

from openai import OpenAI

from exceptions import EmptyContentResponseError, ProviderRequestError
from telegram_client.config import config

logger = logging.getLogger(__name__)
logging.basicConfig(filename="gpt_model.log")
logging.getLogger().setLevel(logging.INFO)


class GPTVersion(StrEnum):
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4o = "gpt-4o"
    GPT_4 = "gpt-4-turbo"


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
        self.__client_gpt = OpenAI(
            api_key=config.get("OPEN_AI_API_KEY"),
            organization=config.get("ORGANIZATION_KEY"),
        )
        logger.info("GPT model initialized")

    def ask_gpt(
        self,
        prompt: str,
        user_messages: list = None,
        version: GPTVersion = GPTVersion.GPT_35_TURBO,
    ) -> str:
        """Method for communicating with ChatGPT"""
        try:
            logger.info(f"sending request to GPT {version} provider")
            if user_messages:
                user_messages.append({"role": "user", "content": prompt})
                response = self.__client_gpt.chat.completions.create(
                    model=version,
                    messages=user_messages,
                )
            else:
                response = self.__client_gpt.chat.completions.create(
                    model=version,
                    messages=[{"role": "user", "content": prompt}],
                )
            logger.info(f"response from GPT {version} provider recieved")

            response_content = response.choices[0].message.content

            if response_content:
                logger.info(
                    f"Response from GPT {version} provider returned to the user"
                )
                return response_content
            else:
                logger.error(f"there is no message content from GPT {version} provider")
                raise EmptyContentResponseError(
                    "There is no response from ChatGPT, try to send the message again."
                )
        except Exception as exc:
            logger.error(
                f"There is an error with sending request to GPT {version} provider {repr(exc)}"
            )
            raise ProviderRequestError(
                f"There is an error with sending request to provider {repr(exc)}"
            )
