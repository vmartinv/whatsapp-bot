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
Vaco can do all this stuff:
/search <term>: Searches in google
/search <term> #3: Searches in google and gets the third result (can use other index)
/around <term>: Searches in google maps <term> using the last location provided.
/camera: Takes a picture with the server camera and sends it
/video <duration> <fps>: Takes a video with the server camera and sends it. Arguments are optional.
/url <some_url>: Sends a screenshot of a web page
/tts <text>: Text to speech
/tts_lang <language>: Set /tts language. Example: /tts_lang es, /tts_lang en, etc
/play: Plays the last audio sent through the server speaker
/ping: Replies pong
/help: Prints this help
""".strip())
