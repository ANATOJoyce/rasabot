import asyncio
import inspect
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn

import rasa.utils.endpoints 
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

class MyIO( TelegramInput):
    @classmethod
    def name(cls) -> Text:
        return "myio"

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:

        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            try:
                sender_id = request.json.get("sender", "anonymous")
                text = request.json.get("text", "")
                metadata = self.get_metadata(request)

                collector = CollectingOutputChannel()

                await on_new_message(
                    UserMessage(
                        text,
                        collector,
                        sender_id,
                        input_channel=self.name(),
                        metadata=metadata,
                    )
                )

                return response.json(collector.messages)

            except Exception as e:
                return response.json({"error": str(e)}, status=500)

        return custom_webhook
