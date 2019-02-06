#!/usr/bin/python2
#Import necessary modules
#selenium was installed in order to use this
#webdriver for google chrome was also installed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import image2camera
from urllib2 import urlopen
import scipy.misc as misc
import cv2
import numpy as np
import io
import re
from PIL import Image
import os.path
import logging
from router import RouteLayer
from views.message import Message
import os
import pyperclip
import subprocess
import time

logging.basicConfig(filename="whatsappbot.log", level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        for i,fn in enumerate(self.ecs):
            try:
                res = fn(driver)
                if res: return (i,res)
            except:
                pass

class WhatsappBot():
    def __init__(self, user_data):
        self.router = RouteLayer()
        chrome_options = Options()
        chrome_options.add_argument("user-data-dir="+user_data) 

        #chrome webdriver opened by python.
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        #Load up Web Whatsapp
        self.driver.get("https://web.whatsapp.com/")

        wait_load = WebDriverWait(self.driver, 99999)

        qr_path =  "//img[contains(@alt,'Scan me!')]"
        x_arg = "//span[@data-icon='menu']"

        i, detected_element = wait_load.until(AnyEc(
            EC.presence_of_element_located((By.XPATH, qr_path)),
            EC.presence_of_element_located((By.XPATH, x_arg)),
            ))
        if i==0:
            qr_image = detected_element
            logging.info("located the qr")

            # now that we have the preliminary stuff out of the way time to get that image :D
            location = qr_image.location
            size = qr_image.size
            png = self.driver.get_screenshot_as_png() # saves screenshot of entire page
            im = Image.open(io.BytesIO(png)) # uses PIL library to open image in memory
            left = location['x']
            top = location['y']
            right = location['x'] + size['width']
            bottom = location['y'] + size['height']
            im = im.crop((left, top, right, bottom)) # defines crop points

            qr_im = np.array(im)

            qr_thread = image2camera.SendImageJob(qr_im, "/dev/video2")
            qr_thread.start()


            logging.info("started camera")
            
            #Provide time to scan whatsapp QR code
            wait_scan = WebDriverWait(self.driver, 300)

            #wait for load
            wait_scan.until(EC.presence_of_element_located((
                By.XPATH, x_arg)))

            if qr_image:
                qr_thread.shutdown_flag.set()
                qr_thread.join()

        logging.info("logged in to whatsapp web")
    
    def loop(self):
        wait_message = WebDriverWait(self.driver, 5)
        msg_xpath = "//span[contains(@title, '/')]"
        while True:
            try:
                new_message = wait_message.until(EC.presence_of_element_located((
                    By.XPATH, msg_xpath)))
            except TimeoutException:
                logging.info("no messages")
                new_message = None
            if new_message:
                sender = new_message.find_element_by_xpath("../../..//span[contains(@title, '')]")
                msg = Message(sender.text, new_message.text)
                new_message.click()
                self.handle_message(msg)
            time.sleep(5) # seconds
        
    
    def handle_message(self, msg):
        answer = self.router.route(self.driver, msg)
        if answer:
            wait_load = WebDriverWait(self.driver, 1)
            if answer.type == "text":
                inp = "//div[@contenteditable='true']"
                input_box = wait_load.until(EC.presence_of_element_located((
                    By.XPATH, inp)))
                input_box.send_keys(answer.data.replace("\n", Keys.SHIFT + Keys.ENTER + Keys.SHIFT) + Keys.ENTER)
            elif answer.type.startswith("image/") or answer.type.startswith("video/"):
                try:
                    # we simulate a file drag and drop
                    # can get broken if whatsapp UI changes
                    js_script = """
var candidates = document.getElementsByClassName('vW7d1');
var target = candidates[candidates.length - 1];
var offsetX = 337,
offsetY = 17;

var input = document.createElement('input');
input.type = 'file';
input.style.display = 'none';
input.onchange = function () {
target.scrollIntoView(true);

var rect = target.getBoundingClientRect(),
x = rect.left + (offsetX || (rect.width >> 1)),
y = rect.top + (offsetY || (rect.height >> 1)),
dataTransfer = { files: this.files , items : {kind : "file", type: \"""" + answer.type + """\"}, types : ["Files"] };

[['dragenter', 'vW7d1'], ['dragleave', 'NuJ4j'], ['drop', '_3TSht']].forEach(function (name) {
    var candidates = document.getElementsByClassName(name[1]);
    var target = candidates[candidates.length - 1];
    var evt = document.createEvent('MouseEvent');
    evt.initMouseEvent(name[0], !0, !0, window, 0, 630, 630, x, y, !1, !1, !1, !1, 0, target);
    evt.dataTransfer = dataTransfer;
    evt.isTrusted = !0;
    target.dispatchEvent(evt);
});

setTimeout(function () { document.body.removeChild(input); }, 25);
};
document.body.appendChild(input);
return input;
"""
                    input_file = self.driver.execute_script(js_script)
                    input_file.send_keys(os.path.abspath(answer.data))
                    send_button_xpath = "//span[@data-icon='send-light']/.."
                    wait_upload = WebDriverWait(self.driver, 10)
                    send_button = wait_upload.until(EC.presence_of_element_located((
                        By.XPATH, send_button_xpath)))
                    send_button.click()
                    
                    # This code simulates attaching the file
                    # by using the clipboard and
                    # simulating OS keyboard presses.
                    # Always works but you shouldnt use the computer if you
                    # run the bot, as it can interfere .
                    # ~ attach_button = "//div[@title='Attach']"
                    # ~ wait_load.until(EC.presence_of_element_located((
                        # ~ By.XPATH, attach_button))).click()
                    
                    # ~ image/*,video/mp4,video/3gpp,video/quicktime
                    # ~ inp = "//input[contains(@accept, 'image/*')]/.."
                    # ~ input_box = wait_load.until(EC.presence_of_element_located((
                        # ~ By.XPATH, inp)))
                    
                    # ~ input_box.click()
                    # ~ pyperclip.copy(answer.data)
                    # ~ subprocess.check_call("xdotool key --clearmodifiers ctrl+v key KP_Enter".split(" "))
                    # ~ send_button_xpath = "//span[@data-icon='send-light']/.."
                    # ~ wait_upload = WebDriverWait(self.driver, 10)
                    # ~ send_button = wait_upload.until(EC.presence_of_element_located((
                        # ~ By.XPATH, send_button_xpath)))
                    # ~ send_button.click()
                    # ~ time.sleep(1)
                    # ~ wait_load.until(EC.presence_of_element_located((
                        # ~ By.XPATH, attach_button))).click()
                except Exception as e:
                    logging.exception("Error sending picture %s to %s:%s" % (answer.data, msg.sender, e))
            else:
                log.error("Unkown message response 23423")

    def quit(self):
        self.driver.quit()

def main():
    bot = WhatsappBot("selenium")
    bot.loop()
    

if __name__=="__main__":
    main()

