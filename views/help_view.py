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
/search <term>: Searches in google
/search <term> #3: Searches in google and gets the third result (can use other index)
/around <term>: Searchs in google maps <term> using the last location provided.
/camera: Takes a picture with the server camera and sends it
/video <duration> <fps>: Takes a video with the server camera and sends it. Arguments are optionals.
/play: Plays the last audio sent through the server speaker
/ping: Replies pong
""".strip())
