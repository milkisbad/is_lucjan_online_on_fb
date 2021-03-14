# The Facebook Online Friend Tracker
# Author: Baraa Hamodi

import csv
import getpass
import os
import time
import json
import mariadb
import datetime

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

SLEEP = 10  # in seconds
IMPLICIT_WAIT = 20  # in seconds


print('start')
conn = mariadb.connect(
    user="patryk",
    password="root",
    host="localhost",
    database="is_lucjan_online_database")
conn.autocommit = True

cur = conn.cursor()

# Enable tab completion for raw input.
try:
  import readline
  readline.parse_and_bind('tab: complete')
except ImportError:
  pass

# Support both Python 2.x and 3.x user input functions.
try:
  input = raw_input
except NameError:
  pass

def main():
  # load config
  config = json.load(open('./config.json'))
  print(config)
  # Prompt user for Facebook credentials.
  print('\nFacebook Online Friend Tracker starting...')
  facebook_username = input('Facebook username: ')
  facebook_password = getpass.getpass('Facebook password: ')

  interval_time = config['interval_time']
  print(f"interval_time {interval_time} minutes")
  interval_time = interval_time * 60

  # Initialize Chrome WebDriver.
  print('\nInitializing Chrome WebDriver...')
  driver = webdriver.Chrome()

  # Change default timeout and window size.
  driver.implicitly_wait(IMPLICIT_WAIT)
  driver.set_window_size(700, 500)

  # Go to www.facebook.com and log in using the provided credentials.
  print('Logging into Facebook...')
  driver.get('https://www.facebook.com/')
  emailBox = driver.find_element_by_id('email')
  emailBox.send_keys(facebook_username)
  passwordBox = driver.find_element_by_id('pass')
  passwordBox.send_keys(facebook_password)

  wait = WebDriverWait(driver, 10)
  wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Accept All']"))).click()
  wait1 = WebDriverWait(driver, 10)
  wait1.until(EC.element_to_be_clickable((By.XPATH, "//button"))).click()

  while True:
    # Wait for Facebook to update the number of online friends.
    print(f'\nat astart of iteration, sleeping {SLEEP} seconds')
    time.sleep(SLEEP)

    # Scrape if online
    found_online = 0
    print('checking if online')
    try:
      is_online = driver.find_element_by_xpath('//*[text()="Lucjan Dybczak"]//..//..//..//..//..//..//span[contains(@class, "pq6dq46d jllm4f4h qu0x051f esr5mh6w e9989ue4 r7d6kgcz s45kfl79 emlxlaya bkmhp75w spb7xbtv t6na6p9t c9rrlmt1")]')
      print('checked')
      if is_online:
        is_online = 1
        found_online = 1
    except:
      is_online = 0
    print('Done! Detected ' + str(is_online))

    # Get current time.
    today = datetime.now()

    try:
      cur.execute("INSERT INTO lucjan_data (date, is_online) VALUES (?, ?)", (today, is_online))
      print(f"added ({today}, {is_online}")
    except mariadb.Error as e:
      print(f"Error: {e}")

    # Wait for next interval and increment iteration counter.
    time.sleep(interval_time - SLEEP - (1-found_online)*IMPLICIT_WAIT)
