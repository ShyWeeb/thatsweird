from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import random
import time
import os
import json
import re

videos = []

def add_videos(old_data, new_data):
    for nd in new_data:
        videoID = nd["videoID"]
        for od in old_data:
            if od["videoID"] == videoID:
                if od != nd:
                    od.update(nd)
        old_data.append(nd)
    return old_data

def save(data):
    path = os.path.join(os.getcwd(), 'db.json')
    if os.path.isfile(path):
        file = open(path, 'r', encoding='utf8')
        old_data = json.load(file)
        new_data = add_videos(old_data, data)
        file.close()

        file = open(path, 'w', encoding='utf8')
        json.dump(new_data, file, indent=4, ensure_ascii=False)
        file.close()
        print("DUMPED!")
    else:
        file = open(path, 'w', encoding='utf8')
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.close()
        print("DUMPED!")

def cookie_check(driver):
    while True:
        if driver.current_url.startswith('https://consent.youtube.com'):
            driver.find_element(By.XPATH, '/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/form[1]/div/div/button').click()
            time.sleep(1)
        else:
            return

def get_youtube_video_id(url):
  match = re.search(r"(?:v=|\/embed\/)([a-zA-Z0-9_-]+)", url)
  if match:
    return match.group(1)
  else:
    return None

def empty_type_check(d):
    return any(value is None or value == "" for value in d.values())

def scrape_exit_check(driver, contents_div, contents_count, scrape_result):
    count = 1

    driver.execute_script("arguments[0].scrollIntoView();", scrape_result[-1])

    while count <= 5:
        time.sleep(1)
        contents = contents_div.find_elements(By.ID, 'content')
        if len(contents) == contents_count:
            count+=1
        else:
            return False
        
    return True

def scrape_videos(driver, contents):
    for content in contents:
        container = content.find_element(By.ID, 'container')
        thumbnail_e = container.find_element(By.CSS_SELECTOR, "a#thumbnail")
        thumbnail_url = thumbnail_e.find_element(By.TAG_NAME, 'img').get_attribute('src')
        if thumbnail_url == None:
            count = 1
            while True:
                if count <= 5:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'end', inline: 'end' });", 
                        thumbnail_e
                    )
                    time.sleep(0.1)
                    thumbnail_url = thumbnail_e.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    if thumbnail_url != None:
                        break
                    else:
                        print(f"THUMBNAIL URL COUNT: {count}")
                        count+=1
                else:
                    print("THUMBNAIL URL DID NOT APPEAR AFTER 5 ATTEMPTS...")
                    break
        overlays = thumbnail_e.find_element(By.ID, 'overlays')
        length_div = overlays.find_element(By.TAG_NAME, 'ytd-thumbnail-overlay-time-status-renderer')
        length_badge_shape = length_div.find_element(By.TAG_NAME, 'badge-shape')
        length = length_badge_shape.find_element(By.TAG_NAME, 'div').text
        if length == '':
            count = 1
            while True:
                if count <= 5:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'end', inline: 'end' });", 
                        length_div
                    )
                    time.sleep(1)
                    length_badge_shape = length_div.find_element(By.TAG_NAME, 'badge-shape')
                    length = length_badge_shape.find_element(By.TAG_NAME, 'div').text
                    if length == '':
                        break
                    else:
                        print(f"LENGTH COUNT: {count}")
                        count+=1
                else:
                    print("LENGTH DID NOT APPEAR AFTER 5 ATTEMPTS...")
                    break
        meta = container.find_element(By.ID, 'meta')
        video_title_e = meta.find_element(By.ID, 'video-title')
        video_title = video_title_e.get_attribute('title')
        video_link = video_title_e.get_attribute('href')
        video_id = get_youtube_video_id(video_link)
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        metadata = container.find_element(By.ID, 'metadata')
        byline_container = metadata.find_element(By.ID, 'byline-container')
        ytd_channel_name = byline_container.find_element(By.TAG_NAME, 'ytd-channel-name')
        ytd_channel_name_text_container = ytd_channel_name.find_element(By.ID, 'text-container')
        channel_e = ytd_channel_name_text_container.find_element(By.TAG_NAME, 'a')
        channel_link = channel_e.get_attribute('href')
        channel_name = channel_e.text
        video_info_e = container.find_element(By.ID, 'video-info')
        video_infos = video_info_e.find_elements(By.TAG_NAME, 'span')
        if len(video_infos) == 3:
            view_count = video_infos[0].text
            upload_date = video_infos[2].text
        else:
            print("BAD LENGTH FOR VIDEO INFOS...")
            return

        e = {
            "title": video_title,
            "videoURL": video_link,
            "videoID": video_id,
            "videoLength": length,
            "viewCount": view_count,
            "shortUploadDate": upload_date,
            "channelName": channel_name,
            "channelURL": channel_link,
            "thumbnailURL": thumbnail_url
        }
        if empty_type_check(e) == True:
            count = 1
            while True:
                if count >= 5:
                    time.sleep(1)
                    if empty_type_check(e) == False:
                        break
                    else:
                        count+=1
                else:
                    print("EMPTY ITEM DID NOT CHANGE AFTER 5 ATTEMPTS...")
                    break
        if e not in videos:
            videos.append(e)

    return contents

def scrape_playlist(playlist_url):
    user_agent = '"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"'
    options = Options()
    options.add_argument(f"--user-agent={user_agent}")
    driver = webdriver.Firefox(options=options)
    driver.get(playlist_url)
    cookie_check(driver)

    while True:
        primary = driver.find_element(By.ID, 'primary')
        contents_div = primary.find_element(By.ID, 'contents')
        contents = contents_div.find_elements(By.ID, 'content')
        contents_count = len(contents)
        scrape_result = scrape_videos(driver, contents)
        
        if scrape_exit_check(driver, contents_div, contents_count, scrape_result) == True:
            break
            
    save(videos)
    driver.quit()

if __name__ == "__main__":
    scrape_playlist("https://www.youtube.com/playlist?list=PLVcLWy6q41jU0pQ9P7LxTYvhVG_nYo4C5")