# -*- coding: utf-8 -*-
"""
    Help view.
"""
from message import Message
from basic_view import View
import logging


class HelpView(View):
    def routes(self):
        return [
            ("/help$", self.print_help),
        ]

    def print_help(self, driver, message, match):
            return Message("bot", u"""
/help: Prints this help
/url <some_url>: Sends a screenshot of a web page
/camera: Takes a picture with the server camera and sends it
/ping: Replies pong
""".strip())
