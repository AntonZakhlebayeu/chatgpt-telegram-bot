from typing import Dict, List

from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler)


class ConversationHandlerFactory:
    def __init__(self, persistent: bool = False):
        self.__persistent = persistent

    def create(
        self,
        entry_points: List[CommandHandler],
        states: Dict[int, List[CallbackQueryHandler]],
        fallbacks: List[CallbackQueryHandler],
        map_to_parent: Dict = {},
        name: str = "default_handler",
    ) -> ConversationHandler:
        return ConversationHandler(
            entry_points=entry_points,
            states=states,
            fallbacks=fallbacks,
            map_to_parent=map_to_parent,
            name=name,
            persistent=self.__persistent,
        )
