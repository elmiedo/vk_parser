import time
import timestring
from lxml import html
from pymongo import MongoClient
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from chromedriver.proxy import IP, PORT, USER, PASS


URL = "https://vk.com/tokyofashion"
DRIVER_PATH = "./chromedriver"
TIMEOUT = 10
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME = 'vk'


options = Options()
options.add_argument("--start-maximized")

proxy = {
    'proxy': {
        'http': f'http://{USER}:{PASS}@{IP}:{PORT}',
        'https': f'http://{USER}:{PASS}@{IP}:{PORT}',
        'no_proxy': 'localhost, 127.0.0.1'
    }
}


def str_to_date(date_string):
    try:
        if date_string:
            return timestring.Date(f'{date_string}').date
    except timestring.TimestringInvalid:
        pass


def find_post(driver: webdriver.Chrome):
    button = driver.find_element(
        By.XPATH, '//*[contains(@class,"ui_tab_plain ui_tab_search")]')
    button.click()
    time.sleep(0.5)
    try:
        search_field = WebDriverWait(driver, timeout=TIMEOUT).until(
            expected_conditions.presence_of_element_located((
                By.ID, "wall_search"
            ))
        )
        search_input = input('Type your search request: ')
        search_field.send_keys(search_input)
        search_field.send_keys(Keys.ENTER)
    except TimeoutException:
        pass
    except Exception as exception:
        print(exception)


def scroll_page(driver: webdriver.Chrome):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        try:
            button = WebDriverWait(driver, timeout=TIMEOUT).until(
                expected_conditions.element_to_be_clickable((
                    By.CLASS_NAME, "UnauthActionBox__close"
                ))
            )
            button.click()
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        except TimeoutException:
            pass
        except Exception as exception:
            print(exception)


def get_value(elements):
    if elements:
        return elements[0]
    return None


def parse_post(elem):
    post_summary = {}
    post = html.fromstring(elem.get_attribute("outerHTML"))
    post_summary['link'] = 'https://vk.com' + get_value(post.xpath(
        '//*[@class="post_link"]/@href'))
    post_summary['date'] = str_to_date(get_value(post.xpath(
        '//*[@class="rel_date"]/text()')).replace('\xa0', ' '))
    post_summary['text'] = ''.join(post.xpath(
        '//*[@class="wall_post_text"]//text()'))
    post_summary['likes'] = get_value(post.xpath(
        "//*[contains(@class,'like_cont')]//div[contains("
        "@class,'PostButtonReactions__title ')]/text()"))
    post_summary['shares'] = get_value(post.xpath(
        "//div[@data-like-button-type = 'share']"
        "//span[contains(@class, 'PostBottomAction__count')]/text()"))
    views = ''.join(post.xpath(
        "//*[contains(@class, 'like_views like_views')]//text()")).replace(
        'K', '').strip()
    if views:
        post_summary['views'] = float(views) * 1000
    photos = post.xpath(
        "//a[contains(@class,'page_post_thumb_')]/@data-photo-id")
    if photos:
        post_summary['photo_links'] = [
            'https://vk.com/photo' + photo for photo in photos]
    videos = post.xpath("//a[contains(@class,'page_post_thumb_')]/@href")
    if videos:
        post_summary['video_links'] = [
            'https://vk.com/' + video for video in videos]
    return post_summary


def save_to_mongo(data, db_name, db_collection, db_host=None, db_port=None):
    with MongoClient(host=db_host, port=db_port) as client:
        db = client[db_name]
        db.get_collection(db_collection).update_one(
            {'link': data['link']}, {'$set': data}, upsert=True)


if __name__ == '__main__':
    driver_service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(
        service=driver_service, options=options, seleniumwire_options=proxy)
    driver.get(URL)
    find_post(driver=driver)
    scroll_page(driver=driver)
    time.sleep(10)
    posts = driver.find_elements(By.XPATH, '//*[@class="_post_content"]')
    for items in posts:
        parse_summary = parse_post(items)
        save_to_mongo(parse_summary, DB_NAME, 'tokyofashion')
