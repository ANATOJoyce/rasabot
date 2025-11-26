import asyncio
import inspect
# from sanic import Sanic, Blueprint, response
# from sanic.request import Request
# from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn

# import rasa.utils.endpoints 
# from rasa.core.channels.channel import (
#     InputChannel,
#     CollectingOutputChannel,
#     UserMessage,
# )
from rasa.core.channels.telegram import TelegramInput

class MyIO(TelegramInput):
    @classmethod
    def name(cls) -> Text:
        return "myio"