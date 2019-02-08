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
import utils
import logging
import requests
from BeautifulSoup import BeautifulSoup
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class GoogleViews():
    def __init__(self):
        self.cache = {}
        self.last = None
        self.maps_location_re = re.compile("^https://maps.google.com/maps\?q=(?P<lat>-?\d+\.\d+)%2C(?P<long>-?\d+\.\d+)&z=(?P<z>-?\d+)")

    def routes(self):
        return [
            # ~ (".*https?:\/\/(?:www\.|m\.)?youtu(?:be.com\/watch\?v=|\.be/)(?P<video_id>[\w-]+)(&\S*)?$",
             # ~ self.send_yt_video),
            ("/s(earch)?\s+\#(?P<idx>[^$]+)$", self.google_search_last),
            ("/s(earch)?\s+(?P<term>[^\#$]+)(\s+\#(?P<idx>[^$]+))?$", self.google_search),
            ("/a(round)?\s+(?P<term>[^$]+)$", self.search_around_me),
        ]

    # ~ def send_yt_video(self, driver, message, match):
        # ~ self.yt_sender.send_by_url(jid=message.getFrom(), file_url=match.group("video_id"))
    
    def search_around_me(self, driver, message, match):
        location_xpath = "//a[contains(@href,'https://maps.google.com/maps')]"
        wait_upload = WebDriverWait(driver, 15)
        try:
            location = wait_upload.until(EC.presence_of_element_located((
                By.XPATH, location_xpath)))
        except TimeoutException:
            return Message("bot", "You need to send your location first.")
        location = driver.find_elements_by_xpath(location_xpath)[-1]
        coords = self.maps_location_re.match(location.get_attribute("href"))
        term = utils.encode_html(match.group("term"))
        url = "https://www.google.com/maps/search/{0}/@{1},{2},{3}z".format(term, coords.group("lat"), coords.group("long"), coords.group("z"))
        return utils.url_screenshot(driver, url)
    
    @staticmethod
    def get_links(driver):
        rows = driver.find_elements_by_xpath("//div[@class='r']")
        links = [row.find_element_by_tag_name("a").get_attribute("href") for row in rows]
        return links

    def put_cache(self, driver, search_url, result_urls):
        self.cache[search_url]=result_urls

    def get_cache(self, driver, search_url):
        if search_url in self.cache:
            return self.cache[search_url]
        else:
            result_urls = utils.url_read(driver, search_url, GoogleViews.get_links)
            self.cache[search_url] = result_urls
            return result_urls

    def google_search_last(self, driver, message, match):
        search_url = self.last
        if search_url:
            idx = int(match.group("idx")) - 1
            result_urls = self.get_cache(driver, search_url)
            if 0<=idx and idx<len(result_urls):
                return utils.url_screenshot(driver, result_urls[idx])
            else:
                return Message("bot", "Use an index between 1 and %d." % len(result_urls)+1)
        else:
            return Message("bot", "You need to provide a term to search first")

    def google_search(self, driver, message, match):
        term = utils.encode_html(match.group("term"))
        search_url = "https://www.google.com/search?q=%s" % term            
        if(match.group("idx")):
            idx = int(match.group("idx")) - 1
            result_urls = self.get_cache(driver, search_url)
            if 0<=idx and idx<len(result_urls):
                return utils.url_screenshot(driver, result_urls[idx])
            else:
                return Message("bot", "Use an index between 1 and %d." % len(result_urls)+1)
        else:
            def mark_links(driver):
                driver.execute_script("""
var i=0;
[].forEach.call(document.getElementsByClassName("r"), function(el) {
    if(el.tagName=="DIV"){
        var label = document.createElement('div');
        label.innerHTML = "#"+(++i).toString();
        label.style.color= "red";
        label.style.fontSize="300%";
        label.style.float = "right";
        el.insertBefore(label, el.firstChild);
    }
});
//Removes some annoying sections
[].forEach.call(document.getElementsByTagName("g-section-with-header"), function(el) {
    el.outerHTML = "";
});
//Removes search bar
document.querySelectorAll('[jscontroller="ZyRBae"]')[0].outerHTML="";
""")
                element = driver.find_elements_by_class_name('mw')[1]
                screenshot_file = 'image.png'
                element.screenshot(screenshot_file)
                screenshot = Message("bot", screenshot_file, "image/png")
                return screenshot, GoogleViews.get_links(driver)
            screenshot, result_urls  = utils.url_read(driver, search_url, mark_links)
            self.put_cache(driver, search_url, result_urls)
            self.last = search_url
            return screenshot

