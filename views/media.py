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
import logging
import time


class MediaViews(View):
    def routes(self):
        """
            Creates the regex routes and callbacks to handle media messages
        """
        return [
            ("/url https?:\/\/(?:[\w\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:jpe?g|gif|png)($|\?[^\s]+$)", self.send_image),
            ("/url https?:\/\/(?:[\w\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:mp4|webm)($|\?[^\s]+$)", self.send_video),
            ("/url https?:\/\/[^$]+$", self.send_url_print),
            # ~ ("^/t(ts)?\s(?P<tts_text>[^$]+)$", self.send_tts)
        ]

    def send_video(self, driver, message, match):
        img_url = message.data[len("/url "):]
        # ~ try:
        image_on_web = urllib.urlopen(img_url)
        if image_on_web.info().type ==  'video/mp4':
            extension = "mp4"
        elif image_on_web.info().type == 'video/webm':
            extension = "webm"
        else:
            return Message("bot", u"error downloading video")     
        buf = image_on_web.read()
        file_path = "%s.%s" % ("image", extension)
        downloaded_image = file(file_path, "wb")
        downloaded_image.write(buf)
        downloaded_image.close()
        image_on_web.close()
        return Message("bot", file_path, "image")
        # ~ except:
            # ~ return Message("bot", u"error downloading image")

    def send_image(self, driver, message, match):
        img_url = message.data[len("/url "):]
        try:
            image_on_web = urllib.urlopen(img_url)
            if image_on_web.info().type == 'image/jpeg':
                extension = "jpg"
            elif image_on_web.info().type == 'image/png':
                extension = "png"
            elif image_on_web.info().type == 'image/gif':
                extension = "gif"
            else:
                return Message("bot", u"error downloading image")     
            buf = image_on_web.read()
            file_path = "%s.%s" % ("image", extension)
            downloaded_image = file(file_path, "wb")
            downloaded_image.write(buf)
            downloaded_image.close()
            image_on_web.close()
            return Message("bot", file_path, image_on_web.info().type)
        except:
            return Message("bot", u"error downloading image")
    
    @staticmethod
    def url_print(driver, web_url):
        try:
            main_window = driver.current_window_handle
            driver.execute_script('''window.open("{}","_blank");'''.format(web_url))
            time.sleep(0.5)
            driver.switch_to_window(driver.window_handles[-1])
            try:
                WebDriverWait(driver, 5).until(
                          lambda driver: driver.execute_script("return document.readyState") == "complete")
            except:
                pass
            screenshot_file = 'image.png'
            driver.save_screenshot(screenshot_file)
            driver.close()
            driver.switch_to_window(main_window)
            return Message("bot", screenshot_file, "image/png")
        except:
            return Message("bot", u"error downloading image")
    
    def send_url_print(self, driver, message, match):
        web_url = message.data[len("/url "):]
        return MediaViews.url_print(driver, web_url)

    # ~ def send_tts(self, driver, message, match):
        # ~ tts_text = match.group("tts_text")
        # ~ return self.tts_sender.send(text=tts_text)
