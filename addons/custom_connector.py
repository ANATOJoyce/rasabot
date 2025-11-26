import asyncio
import inspect
# from sanic import Sanic, Blueprint, response
# from sanic.request import Request
# from sanic.response import HTTPResponse
import typing
from typing import List, Text, Dict, Any, Optional, Callable, Awaitable, NoReturn, Union

# import rasa.utils.endpoints 
# from rasa.core.channels.channel import (
#     InputChannel,
#     CollectingOutputChannel,
#     UserMessage,
# )
from aiogram.bot.api import check_result
from rasa.core.channels.telegram import TelegramInput, TelegramOutput, TelegramAPIError
from rasa.shared.exceptions import RasaException
import requests
from aiogram import types
from aiogram.types import User, Message
from aiogram.utils.payload import prepare_arg, generate_payload
from aiogram.bot.base import base

class MyOutput(TelegramOutput):
    def __init__(self, access_token: Optional[Text]) -> None:
        super().__init__(access_token)
        self.base_url = f"https://api.telegram.org/bot{access_token}"
    @classmethod
    def name(cls) -> Text:
        return "telegram"
    
    def camel_case(value: str) -> str:
        parts = value.lower().split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])


    async def request(self, method: base.String,
                      data: Optional[Dict] = None,
                      files: Optional[Dict] = None, **kwargs) -> Union[List, Dict, base.Boolean]:

        url = f"{self.base_url}/{method}"

        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=data, files=files)
            return response.json().get("result")
        except Exception as e:
            raise e
        
    
    async def get_me(self) -> Dict[Text, Any]:
        """Fetches information about the bot from Telegram."""
        url = f"{self.base_url}/getMe"

        payload = ""
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        response_body = response.json()
        result = response_body.get("result")
        print("Bot info:", result)
        return User(**result)

    async def send_message(self,
                           chat_id: typing.Union[base.Integer, base.String],
                           text: base.String,
                           parse_mode: typing.Optional[base.String] = None,
                           entities: typing.Optional[typing.List[types.MessageEntity]] = None,
                           disable_web_page_preview: typing.Optional[base.Boolean] = None,
                           disable_notification: typing.Optional[base.Boolean] = None,
                           reply_to_message_id: typing.Optional[base.Integer] = None,
                           allow_sending_without_reply: typing.Optional[base.Boolean] = None,
                           reply_markup: typing.Union[types.InlineKeyboardMarkup,
                                                      types.ReplyKeyboardMarkup,
                                                      types.ReplyKeyboardRemove,
                                                      types.ForceReply, None] = None,
                           ) -> Message:
        reply_markup = prepare_arg(reply_markup)
        entities = prepare_arg(entities)
        payload = generate_payload(**locals())
        if self.parse_mode and entities is None:
            payload.setdefault('parse_mode', self.parse_mode)
        url = f"{self.base_url}/sendMessage"
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        response_body = response.json()
        result = response_body.get("result")
        return Message(**result)

class MyIO(TelegramInput):
    @classmethod
    def name(cls) -> Text:
        return "myio"
    
    def get_output_channel(self) -> MyOutput:
        """Loads the telegram channel."""
        channel = MyOutput(self.access_token)

        try:
            asyncio.run(channel.set_webhook(url=self.webhook_url))
        except TelegramAPIError as error:
            raise RasaException(
                "Failed to set channel webhook: " + str(error)
            ) from error

        return channel