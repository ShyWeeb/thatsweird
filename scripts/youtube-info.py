from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import random
import time
import os
import json
import re

def cookie_check(driver):
    try:
        time.sleep(1)
        consent_e = driver.find_element(By.TAG_NAME, 'ytd-consent-bump-v2-lightbox')
        buttons_div = consent_e.find_element(By.CLASS_NAME, 'eom-buttons')
        button_e = buttons_div.find_element(By.CLASS_NAME, 'eom-button-row')
        button = button_e.find_element(By.TAG_NAME, 'button').click()
        time.sleep(1)
    except NoSuchElementException:
        return

def get_youtube_video_id(url):
    match = re.search(r"(?:v=|\/embed\/)([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    else:
        return None

def scrape_video_info(driver, url):
    driver.get(url)
    cookie_check(driver)
    above_the_fold = driver.find_element(By.ID, 'above-the-fold')
    title_div = above_the_fold.find_element(By.ID, 'title')
    title = title_div.find_element(By.TAG_NAME, 'yt-formatted-string').get_attribute('title')
    upload_info = driver.find_element(By.ID, 'upload-info')
    channel_info_div = upload_info.find_element(By.TAG_NAME, 'yt-formatted-string')
    channel_info = channel_info_div.find_element(By.TAG_NAME, 'a')
    channel_name = channel_info.text
    channel_link = channel_info.get_attribute('href')
    info_container = driver.find_element(By.ID, 'info-container')
    info = info_container.find_element(By.ID, 'info')
    infos = info.find_elements(By.TAG_NAME, 'span')
    views = infos[0].text
    date = infos[2].text

    e = {
        "title": title,
        "channelName": channel_name,
        "channelLink": channel_link,
        "views": views,
        "date": date
    }
    print(e)

    driver.quit()

def main():
    url = "https://www.youtube.com/watch?v=RGD9j7AL1Co"

    user_agent = '"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"'
    options = Options()
    options.add_argument(f"--user-agent={user_agent}")
    driver = webdriver.Firefox(options=options)
    scrape_video_info(driver, url)

if __name__ == "__main__":
    main()