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
import cgi
import sys
from selenium import webdriver
import os
from PIL import Image

def encode_html(text):
    return cgi.escape(text).replace(" ", "+")

def url_read(driver, web_url, fun = lambda driver: None):
    main_window = driver.current_window_handle
    driver.execute_script('''window.open("about:blank","_blank");''')
    driver.switch_to_window(driver.window_handles[-1])
    driver.get(web_url)
    try:
        WebDriverWait(driver, 5).until(
                  lambda driver: driver.execute_script("return document.readyState") == "complete")
    except:
        pass
    ret = fun(driver)
    driver.close()
    driver.switch_to_window(main_window)
    return ret

def url_screenshot(driver, web_url, fun2 = lambda driver: None):
    screenshot_file = 'image.png'
    def fun(driver):
        ret = fun2(driver)
        driver.save_screenshot(screenshot_file)
        return ret
    ret = url_read(driver, web_url, fun)
    screenshot = Message("bot", screenshot_file, "image/png")
    if ret is not None:
        return screenshot, ret
    return screenshot

def save_media(media_url):
    media_on_web = urllib.urlopen(media_url)
    mime_type = media_on_web.info().type
    if mime_type == 'image/jpeg':
        extension = "jpg"
    elif mime_type == 'image/png':
        extension = "png"
    elif mime_type == 'image/gif':
        extension = "gif"
    elif mime_type == 'video/mp4':
        extension = "mp4"
    elif mime_type == 'video/webm':
        extension = "webm"
    else:
        return Message("bot", u"error downloading media")
    buf = media_on_web.read()
    file_path = "%s.%s" % ("tmp", extension)
    downloaded_media = file(file_path, "wb")
    downloaded_media.write(buf)
    downloaded_media.close()
    media_on_web.close()
    return Message("bot", file_path, mime_type)


# Taken from
# https://stackoverflow.com/questions/41721734/take-screenshot-of-full-page-with-selenium-python-with-chromedriver
def fullpage_screenshot(driver, file):
        logging.info("Starting chrome full page screenshot workaround ...")

        total_width = driver.execute_script("return document.body.offsetWidth")
        total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
        viewport_width = driver.execute_script("return document.body.clientWidth")
        viewport_height = driver.execute_script("return window.innerHeight")
        print("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height,viewport_width,viewport_height))
        rectangles = []

        i = 0
        while i < total_height:
            ii = 0
            top_height = i + viewport_height

            if top_height > total_height:
                top_height = total_height

            while ii < total_width:
                top_width = ii + viewport_width

                if top_width > total_width:
                    top_width = total_width

                logging.debug("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
                rectangles.append((ii, i, top_width,top_height))

                ii = ii + viewport_width

            i = i + viewport_height

        stitched_image = Image.new('RGB', (total_width, total_height))
        previous = None
        part = 0

        for rectangle in rectangles:
            if not previous is None:
                driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
                time.sleep(0.2)
                driver.execute_script("""
var nav = document.getElementById('topnav');
if(nav) nav.setAttribute('style', 'position: absolute; top: 0px;');
""")
                time.sleep(0.2)
                print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
                time.sleep(0.2)

            file_name = "part_{0}.png".format(part)
            logging.debug("Capturing {0} ...".format(file_name))

            driver.get_screenshot_as_file(file_name)
            screenshot = Image.open(file_name)

            if rectangle[1] + viewport_height > total_height:
                offset = (rectangle[0], total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])

            logging.debug("Adding to stitched image with offset ({0}, {1})".format(offset[0],offset[1]))
            stitched_image.paste(screenshot, offset)

            del screenshot
            os.remove(file_name)
            part = part + 1
            previous = rectangle

        stitched_image.save(file)
        logging.debug("Finishing chrome full page screenshot workaround...")
        return True


# for tests
def main():
    driver = webdriver.Chrome()

    ''' Generate document-height screenshot '''
    url = "http://effbot.org/imagingbook/introduction.htm"
    url = "http://www.w3schools.com/js/default.asp"
    driver.get(url)
    fullpage_screenshot(driver, "test1236.png")
    

if __name__=="__main__":
    main()
