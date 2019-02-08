# -*- coding: utf-8 -*-
"""
    Media download request views.
    Handles the media url messages with utilities classes for it.
"""
import urllib
from message import Message
from basic_view import View
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging
import time
import utils


class MediaViews(View):
    def routes(self):
        """
            Creates the regex routes and callbacks to handle media messages
        """
        return [
            ("/url (?P<url>https?:\/\/(?:[\w\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:jpe?g|gif|png|mp4|webm)($|\?[^\s]+$))", self.send_media),
            ("/url (?P<url>https?:\/\/[^$]+$)", self.send_url_print),
            ("/play", self.play_last_audio),
            # ~ ("^/t(ts)?\s(?P<tts_text>[^$]+)$", self.send_tts)
        ]

    def send_media(self, driver, message, match):
        return utils.save_media(driver, match.group("url"))
    
    def send_url_print(self, driver, message, match):
        return utils.url_screenshot(driver,  match.group("url"))
    
    def play_last_audio(self, driver, message, match):
        play_button_xpath = "//span[@data-icon='audio-play']/.."
        wait_upload = WebDriverWait(driver, 15)
        try:
            play_button = wait_upload.until(EC.presence_of_element_located((
                By.XPATH, play_button_xpath)))
        except TimeoutException:
            return Message("bot", "I couldn't find any audio to play, maybe is hasn't been loaded yet.")
        play_button = driver.find_elements_by_xpath(play_button_xpath)[-1]
        play_button.click()
        return Message("bot", "Played!")

    # ~ def send_tts(self, driver, message, match):
        # ~ tts_text = match.group("tts_text")
        # ~ return self.tts_sender.send(text=tts_text)
