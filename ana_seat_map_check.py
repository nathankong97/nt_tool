from united_airlines import UnitedAirlines
from proxy.proxy import Proxy

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from bs4 import BeautifulSoup
import time


def click_element_by_xpath(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    element.click()
    time.sleep(1)


def has_span_with_text(tag):
    return tag.name == 'a' and tag.find('span', text='選択可')


date = "2023-12-08"
departure_mapping = [
    ("SFO", "00:20"),
    ("JFK", "00:50"),
    ("IAD", "11:05"),
    ("LAX", "00:05"),
    ("ORD", "10:30")
]

proxy = Proxy()

for airport, departure_time in departure_mapping:
    start = time.time()
    ua = UnitedAirlines(proxy)
    ua.driver.get("https://www.ana.co.jp/")

    elem = ua.driver.find_element("xpath", '//button[contains(@id, "be-primary-tab__item2")]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath",
                                  '//button[contains(@class, "be-overseas-reserve-ticket-departure-airport__button")]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '//input[contains(@class, "be-list-with-search__searchbox-input")]')
    elem.send_keys(airport)

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '//ul[contains(@class, "be-list be-list--suggest")]//li')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath",
                                  '//button[contains(@class, "be-overseas-reserve-ticket-arrival-airport__button")]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '//input[contains(@class, "be-list-with-search__searchbox-input")]')
    elem.send_keys("TYO")

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '//ul[contains(@class, "be-list be-list--suggest")]//li')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '(//div[contains(@class, "be-overseas-reserve-ticket-boarding-date")])[1]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '//li[@data-value="ONE_WAY"]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", f'//div[@title="{date}"]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath",
                                  '//button[contains(@class, "be-dialog__button be-dialog__button--positive")]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '//div[contains(@class, "js-be-overseas-reserve-ticket-boarding-class")]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '//li[@data-value="BUS"]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '//button[contains(@class, "be-overseas-reserve-ticket-submit__button")]')
    elem.click()

    time.sleep(1)
    wait(ua.driver, 30).until(EC.presence_of_element_located(("xpath", "//div[contains(@class, 'oneWayDisplayPlan')]")))
    elem = ua.driver.find_element("xpath",
                                  f'((//*[contains(text(), "{departure_time}")])[1]/ancestor::div[@class="oneWayDisplayPlan"]//i[@role="button"])[1]')
    elem.click()

    time.sleep(1)
    elem = ua.driver.find_element("xpath", '(//a[@class="seatMap"])[1]')
    elem.click()

    time.sleep(2)
    ua.driver.switch_to.window(ua.driver.window_handles[1])
    wait(ua.driver, 30).until(EC.presence_of_element_located(("xpath", "//div[contains(@class, 'seatMapWrapper')]")))

    html = ua.driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    seat_map = soup.find_all('table')[0]

    result = seat_map.find_all(has_span_with_text)
    end = time.time()
    print(airport, len(result))
    print(f"Run time {end - start}")
    ua.driver.quit()
    del ua

    time.sleep(2)
