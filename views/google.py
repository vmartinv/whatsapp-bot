# -*- coding: utf-8 -*-
"""
    GoogleViews:
    /s(earch) <term>
    /i(mage) <term>
    youtube urls
"""
import urllib
from message import Message
from basic_view import View
from media import MediaViews
import logging
import requests
from xml.sax.saxutils import escape, unescape
import cgi
from BeautifulSoup import BeautifulSoup
import time

class GoogleViews():
    def routes(self):
        return [
            # ~ (".*https?:\/\/(?:www\.|m\.)?youtu(?:be.com\/watch\?v=|\.be/)(?P<video_id>[\w-]+)(&\S*)?$",
             # ~ self.send_yt_video),
            ("/s(earch)?\s+(?P<term>[^-$]+)(\s+\-(?P<idx>[^$]+))?$", self.google_search),
        ]

    # ~ def send_yt_video(self, driver, message, match):
        # ~ self.yt_sender.send_by_url(jid=message.getFrom(), file_url=match.group("video_id"))

    def google_search(self, driver, message, match):
        if(match.group("idx")):
            idx = int(match.group("idx"))
            
            term = cgi.escape(match.group("term")).replace(" ", "+")
            page_url = "https://www.google.com/search?q=%s" % term
            
            
            main_window = driver.current_window_handle
            driver.execute_script('''window.open("{}","_blank");'''.format(page_url))
            time.sleep(0.5)
            driver.switch_to_window(driver.window_handles[-1])
            try:
                WebDriverWait(driver, 5).until(
                          lambda driver: driver.execute_script("return document.readyState") == "complete")
            except:
                pass
            
            row = driver.find_elements_by_xpath("//div[@class='r']")[idx]
            element = row.find_element_by_tag_name("a")
            result_url = element.get_attribute("href")
            driver.close()
            driver.switch_to_window(main_window)
            return MediaViews.url_print(driver, result_url)
        else:
            term = cgi.escape(match.group("term")).replace(" ", "+")
            page_url = "https://www.google.com/search?q=%s" % term
            return MediaViews.url_print(driver, page_url)

