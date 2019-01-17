#Import necessary modules
#selenium was installed in order to use this
#webdriver for google chrome was also installed
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

#chrome webdriver opened by python. mistakes that can be made which is why sometimes program doesn't work -
#1. not writing 'executable_path=r' (my program failed to run as it did not recognize the format, not a problem on every machine, though)
#2. not writing the .exe :: cannot locate the actual executable driver until you specifiy this
driver = webdriver.Chrome(executable_path=r'add full path until\chromedriver.exe')

#Load up Web Whatsapp
driver.get("https://web.whatsapp.com/")

#Provide time to scan whatsapp QR code
wait = WebDriverWait(driver, 300)

#hello message
hellomessage= "hi! i'm the whatsappbot"

#Enter the name of person or group you want to find. be specific if you have similar names in your directory as it picks the first
#one that appears
target = '"nameofpersonorgroup"'

#this is the format whatsapp follows in order to locate the person/the group you have in your contacts
x_arg = '//span[contains(@title,' + target + ')]'
group_title = wait.until(EC.presence_of_element_located((
	By.XPATH, x_arg)))

#not necessary, only here so i can track progress of program running. alerts after the group/person name has been found
print ("located the group")

#this essentially goes to the chat of the group, accesses the input box
group_title.click()
inp = "//div[@contenteditable='true']"
inp_xpath = '//div[@class="input"][@dir="auto"][@data-tab="1"]'
input_box = wait.until(EC.presence_of_element_located((
	By.XPATH, inp)))

#recursive in case the message needs to be sent more than once
for i in range(1):
	#here, hellomessage is the string with your message, and then enter is pressed to send message
	input_box.send_keys(hellomessage + Keys.ENTER)
	
	#this is so that you don't overwhelm whatsapp lol
	time.sleep(1)



