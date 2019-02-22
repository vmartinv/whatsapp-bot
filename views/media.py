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
from ConfigParser import SafeConfigParser
import subprocess
import os

class EspeakTtsSender():
    """
        Uses espeak to text to speach
    """

    def send(self, sender, text, lang='en'):
        text = text.replace("'", '"')
        file_path = self.tts_record(text, lang)
        opus_file = "image.opus"
        subprocess.check_call(("ffmpeg -y -i {} -c:a libopus {}".format(file_path, opus_file)).split(' '))
        os.remove(file_path)
        return Message(sender, opus_file, "audio/ogg; codecs=opus")

    def tts_record(self, text, lang='en'):
        file_path = "image.wav"
        cmd = "espeak -v%s -w %s '%s'" % (lang, file_path, text)
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).wait()
        return file_path
    
class MediaViews(View):
    SETTINGS_SECTION = "media"
    TTS_LANG_PROP = "tts_lang"
    def __init__(self, settings_file="settings.ini"):
        self.tts_sender = EspeakTtsSender()
        self.settings_file = settings_file
        self.config = SafeConfigParser({self.TTS_LANG_PROP: 'en'})
        self.config.read(settings_file)
        if not self.config.has_section(self.SETTINGS_SECTION):
            self.config.add_section(self.SETTINGS_SECTION)
        lang = self.config.get(self.SETTINGS_SECTION, self.TTS_LANG_PROP)
        self.config.set(self.SETTINGS_SECTION, self.TTS_LANG_PROP, lang)
        
        with open(self.settings_file, 'w') as f:
            self.config.write(f)

    def routes(self):
        """
            Creates the regex routes and callbacks to handle media messages
        """
        return [
            ("/url\s+(?P<url>https?:\/\/(?:[\w\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:jpe?g|gif|png|mp4|webm)($|\?[^\s]+$))", self.send_media),
            ("/url\s+(?P<url>https?:\/\/[^$]+$)", self.send_url_print),
            ("/play$", self.play_last_audio),
            ("^/tts_lang\s+(?P<lang>[^\s$]+)\s*$", self.tts_lang),
            ("^/t(ts)?\s+(?P<tts_text>[^$]+)$", self.send_tts),
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
    
    def tts_lang(self, driver, message, match):
        self.config.read(self.settings_file)
        self.config.set(self.SETTINGS_SECTION, self.TTS_LANG_PROP, match.group("lang"))
        with open(self.settings_file, 'w') as f:
            self.config.write(f)
        return Message(message.sender, "Language set to {}".format(match.group("lang")))

    def send_tts(self, driver, message, match):
        tts_text = match.group("tts_text")
        return self.tts_sender.send(sender=message.sender, text=tts_text, lang=self.config.get(self.SETTINGS_SECTION, self.TTS_LANG_PROP))

# for tests
def main():
    print(EspeakTtsSender().send(text="jenny te amo", lang="es"))

if __name__=="__main__":
    main()
