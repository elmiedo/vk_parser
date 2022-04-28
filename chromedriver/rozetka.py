import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from pprint import pprint

timeout = 10

DRIVER_PATH = "./chromedriver"
driver_service = Service(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=driver_service)


url = "https://rozetka.com.ua/news-articles-promotions/promotions/"
driver.get(url)
driver.refresh()

page = 0

while True:
    try:
        next_promotion = WebDriverWait(driver, timeout=timeout).until(
            expected_conditions.presence_of_element_located((
                By.XPATH, "//span[contains(@class, 'show-more__text')]"))
        )
        time.sleep(2)
        next_promotion.click()
    except Exception as exception:
        print(exception)
        break
    page += 1
    if page > 3:
        break

time.sleep(5)
item = driver.find_elements(
    By.XPATH, "//a[contains(@class, 'promo-tile_state_archive')]")

promo = item[0]
print(promo.text)
print(promo.get_attribute("href"))
img_class = promo.find_element(By.TAG_NAME, "img")
img = img_class.get_attribute("src")
src = driver.page_source
pprint(src)
