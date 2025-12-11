import asyncio
import inspect
# from sanic import Sanic, Blueprint, response
# from sanic.request import Request
# from sanic.response import HTTPResponse
import json
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

BASE_URL = "https://api.telegram.org/bot"

class MyOutput(TelegramOutput):
    
    def __init__(self, access_token: Optional[Text]) -> None:
        self.base_url = f"https://api.telegram.org/bot{access_token}"
        super().__init__(access_token)
        
    @classmethod
    def name(cls) -> Text:
        return "telegram"
    
    # def camel_case(value: str) -> str:
    #     parts = value.lower().split('_')
    #     return parts[0] + ''.join(word.capitalize() for word in parts[1:])


    # async def request(self, method: base.String,
    #                   data: Optional[Dict] = None,
    #                   files: Optional[Dict] = None, **kwargs) -> Union[List, Dict, base.Boolean]:

    #     url = f"{self.base_url}/{method}"

    #     headers = {
    #         'Content-Type': 'application/json'
    #     }
    #     try:
    #         response = requests.request("POST", url, headers=headers, data=data, files=files)
    #         return response.json().get("result")
    #     except Exception as e:
    #         raise e
        
    
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
        print(f"Sending message to chat_id {chat_id}: {text}")
        reply_markup = prepare_arg(reply_markup)
        entities = prepare_arg(entities)
        payload = generate_payload(**{**locals(),"text": text, "chat_id": chat_id})
        if self.parse_mode and entities is None:
            payload.setdefault('parse_mode', self.parse_mode)
        url = f"{self.base_url}/sendMessage"
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

        response_body = response.json()
        print("Send message response: %s", response_body)
        result = response_body.get("result")
        return Message(**result)
    
    async def send_photo(self,
                         chat_id: typing.Union[base.Integer, base.String],
                         photo: typing.Union[base.InputFile, base.String],
                         caption: typing.Optional[base.String] = None,
                         parse_mode: typing.Optional[base.String] = None,
                         caption_entities: typing.Optional[typing.List[types.MessageEntity]] = None,
                         disable_notification: typing.Optional[base.Boolean] = None,
                         reply_to_message_id: typing.Optional[base.Integer] = None,
                         allow_sending_without_reply: typing.Optional[base.Boolean] = None,
                         reply_markup: typing.Union[types.InlineKeyboardMarkup,
                                                    types.ReplyKeyboardMarkup,
                                                    types.ReplyKeyboardRemove,
                                                    types.ForceReply, None] = None,
                         ) -> types.Message:
        """
        Use this method to send photos.

        Source: https://core.telegram.org/bots/api#sendphoto

        :param chat_id: Unique identifier for the target chat or username of the target channel
        :type chat_id: :obj:`typing.Union[base.Integer, base.String]`

        :param photo: Photo to send
        :type photo: :obj:`typing.Union[base.InputFile, base.String]`

        :param caption: Photo caption (may also be used when resending photos by file_id), 0-1024 characters
        :type caption: :obj:`typing.Optional[base.String]`

        :param parse_mode: Send Markdown or HTML, if you want Telegram apps to show bold, italic,
            fixed-width text or inline URLs in your bot's message.
        :type parse_mode: :obj:`typing.Optional[base.String]`

        :param caption_entities: List of special entities that appear in message text,
            which can be specified instead of parse_mode
        :type caption_entities: :obj:`typing.Optional[typing.List[types.MessageEntity]]`

        :param disable_notification: Sends the message silently. Users will receive a notification with no sound
        :type disable_notification: :obj:`typing.Optional[base.Boolean]`

        :param reply_to_message_id: If the message is a reply, ID of the original message
        :type reply_to_message_id: :obj:`typing.Optional[base.Integer]`

        :param allow_sending_without_reply: Pass True, if the message should be sent
            even if the specified replied-to message is not found
        :type allow_sending_without_reply: :obj:`typing.Optional[base.Boolean]`

        :param reply_markup: Additional interface options. A JSON-serialized object for an inline keyboard,
            custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user
        :type reply_markup: :obj:`typing.Union[types.InlineKeyboardMarkup,
            types.ReplyKeyboardMarkup, types.ReplyKeyboardRemove, types.ForceReply, None]`

        :return: On success, the sent Message is returned
        :rtype: :obj:`types.Message`
        """
        reply_markup = prepare_arg(reply_markup)
        caption_entities = prepare_arg(caption_entities)
        payload = generate_payload(**{**locals(), "chat_id":chat_id, "photo": photo})
        if self.parse_mode and caption_entities is None:
            payload.setdefault('parse_mode', self.parse_mode)

        url = f"{self.base_url}/sendPhoto"
        headers = {
            'Content-Type': 'application/json'
        }
        print('image payload')
        print(payload)
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

        response_body = response.json()
        print("Send message response: %s", response_body)
        result = response_body.get("result")
        return Message(**result)
     
    async def send_attachment(
        self, recipient_id: Text, attachment: Text, **kwargs: Any
    ) -> None:
        """Sends an attachment. Default will just post as a string."""
        print(f'send image to ¨{recipient_id}')
        await self.send_photo(recipient_id, attachment)

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