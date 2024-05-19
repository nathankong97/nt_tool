#from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from requests.cookies import cookiejar_from_dict

import datetime
import requests
import time
import logging
import os

from .urls import LOGON_PAGE, LANDING_PAGE
from .endpoints import ACCOUNT_BALANCE_API, EMPLOYEE_API
from util import timing


class SessionManager:
    def __init__(self, ip: str = None) -> None:
        self.driver = None
        self.session = requests.Session()
        self.logged_in = False
        self.options = webdriver.ChromeOptions()
        self.key = None

        self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        #self.options.add_argument("--disable-proxy-certificate-handler")
        #self.options.add_argument('--disable-gpu')
        if ip:
            self.options.add_argument(f'--proxy-server={ip}')
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation", 'enable-logging'])
        self.options.add_experimental_option('useAutomationExtension', False)

        self.initialize_driver()

    def initialize_driver(self):
        os.environ['WDM_LOG_LEVEL'] = '0'
        selenium_logger = logging.getLogger('seleniumwire')
        selenium_logger.setLevel(logging.ERROR)
        self.driver = webdriver.Chrome(service=Service(),
                                       options=self.options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/116.0.0.0 Safari/537.36'})
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.set_window_size(1920, 1080)
        #self.driver.maximize_window()

    def _save_to_session(self):
        driver_cookies = self.driver.get_cookies()
        cookies = {cookie["name"]: cookie["value"] for cookie in driver_cookies}
        self.session.cookies = cookiejar_from_dict(cookies)

    @timing
    def get_token(self):
        url = LANDING_PAGE
        self.driver.get(url)

        request = self.driver.wait_for_request(EMPLOYEE_API, timeout=45)
        headers = request.headers
        self.key = headers["x-authorization-api"]

        self._save_to_session()

    @timing
    def login(self):
        url = LOGON_PAGE
        self.driver.get(url)

        wait(self.driver, 90).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='MileagePlus® number*']")))
        time.sleep(2)
        elem = self.driver.find_element("xpath", "//input[@placeholder='MileagePlus® number*']")
        elem.click()
        elem.send_keys("SJ942934")

        time.sleep(1)
        elem = self.driver.find_element("xpath", "//input[@placeholder='Password*']")
        elem.click()
        elem.send_keys("kfy1997!")

        time.sleep(1)
        elem = self.driver.find_element("xpath", '//button[@type="submit"and contains(@class, "app-components")]')
        elem.click()

        time.sleep(4)
        current_url = self.driver.current_url
        print(current_url)

        if "www.united.com/ual/en/us/account/security/authquestions" in current_url:
            print("Version 1 Auth")
            self.auth_version_1()
        else:
            print("Version 2 Auth")
            self.auth_version_2()

        #wait(self.driver, 90).until(EC.presence_of_element_located((By.XPATH, "//form[@id='bookFlightForm']")))
        request = self.driver.wait_for_request(ACCOUNT_BALANCE_API, timeout=45)
        headers = request.headers
        self.key = headers["x-authorization-api"]
        # self.key = [i.headers for i in self.driver.requests if i.url == ACCOUNT_BALANCE_API][0]["x-authorization-api"]

        self._save_to_session()

    def auth_version_1(self):
        # https://www.united.com/ual/en/us/account/security/authquestions
        wait(self.driver, 90).until(EC.presence_of_element_located((By.XPATH, "//form[@id='authQuestionsForm']")))
        time.sleep(1)

        question1 = self.driver.find_element("xpath", "//*[@id='authQuestionsForm']/div[1]/fieldset/legend")
        if "musical" in question1.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_0__AnswerKey']"))
            select.select_by_visible_text('Piano')
        elif "grew up" in question1.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_0__AnswerKey']"))
            select.select_by_visible_text('Pilot')
        elif "school" in question1.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_0__AnswerKey']"))
            select.select_by_visible_text('Sociology')
        elif "favorite type of music" in question1.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_0__AnswerKey']"))
            select.select_by_visible_text('Pop')
        elif "major city" in question1.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_0__AnswerKey']"))
            select.select_by_visible_text('Detroit')

        time.sleep(0.5)
        question2 = self.driver.find_element("xpath", "//*[@id='authQuestionsForm']/div[2]/fieldset/legend")
        if "musical" in question2.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_1__AnswerKey']"))
            select.select_by_visible_text('Piano')
        elif "grew up" in question2.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_1__AnswerKey']"))
            select.select_by_visible_text('Pilot')
        elif "school" in question2.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_1__AnswerKey']"))
            select.select_by_visible_text('Sociology')
        elif "favorite type of music" in question2.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_1__AnswerKey']"))
            select.select_by_visible_text('Pop')
        elif "major city" in question2.text:
            select = Select(self.driver.find_element("xpath", "//*[@id='QuestionsList_1__AnswerKey']"))
            select.select_by_visible_text('Detroit')

        time.sleep(1)
        elem = self.driver.find_element("xpath", "//input[@id='IsRememberDevice_False']")
        elem.click()

        time.sleep(1)
        elem = self.driver.find_element("xpath", "//button[@id='btnNext']")
        elem.click()

    def auth_version_2(self):
        # https://www.united.com/en/us/account/security/authquestions
        wait(self.driver, 90).until(
            EC.presence_of_element_located((By.XPATH, "//form[contains(@shieldclassname, 'app-components')]")))
        time.sleep(1)

        question1 = self.driver.find_element("xpath",
                                             "(//div[contains(@class, 'MyUnitedAuthQuestions-styles__content')]//label)[1]")
        if "musical" in question1.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[0]']"))
            select.select_by_visible_text('Piano')
        elif "grew up" in question1.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[0]']"))
            select.select_by_visible_text('Pilot')
        elif "school" in question1.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[0]']"))
            select.select_by_visible_text('Sociology')
        elif "favorite type of music" in question1.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[0]']"))
            select.select_by_visible_text('Pop')
        elif "major city" in question1.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[0]']"))
            select.select_by_visible_text('Detroit')

        time.sleep(0.5)
        question2 = self.driver.find_element("xpath",
                                             "(//div[contains(@class, 'MyUnitedAuthQuestions-styles__content')]//label)[2]")
        if "musical" in question2.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[1]']"))
            select.select_by_visible_text('Piano')
        elif "grew up" in question2.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[1]']"))
            select.select_by_visible_text('Pilot')
        elif "school" in question2.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[1]']"))
            select.select_by_visible_text('Sociology')
        elif "favorite type of music" in question2.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[1]']"))
            select.select_by_visible_text('Pop')
        elif "major city" in question2.text:
            select = Select(self.driver.find_element("xpath", "//select[@name='AuthQuestions.questions[1]']"))
            select.select_by_visible_text('Detroit')

        time.sleep(1)
        elem = self.driver.find_element("xpath", "//button[@data-test-id='nextButton']")
        elem.click()

    def initial_search(self):
        today = datetime.date.today()
        day_after_next = today + datetime.timedelta(days=2)
        day_after_next_str = day_after_next.strftime("%b %d, %Y")
        self.driver.get("https://www.united.com/ual/en/us/flight-search/book-a-flight/results")

        wait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//input[@id="RedeemMiles_rMiles"]')))

        elem = self.driver.find_element("xpath", '//label[@for="RedeemMiles_rMiles"]')
        elem.click()
        time.sleep(0.5)

        elem = self.driver.find_element("xpath", '//label[@for="TripTypes_ow"]')
        elem.click()
        time.sleep(2)

        elem = self.driver.find_element("xpath", "//label[@for='Trips_0__Origin']")
        elem.click()
        time.sleep(1)
        elem = self.driver.find_element("xpath", "//input[@id='Trips_0__Origin']")
        elem.send_keys("EWR")
        time.sleep(0.5)

        elem = self.driver.find_element("xpath", "//label[@for='Trips_0__Destination']")
        elem.click()
        time.sleep(1)
        elem = self.driver.find_element("xpath", "//input[@id='Trips_0__Destination']")
        elem.send_keys("ORD")
        time.sleep(0.5)

        elem = self.driver.find_element("xpath", "//label[@for='Trips_0__DepartDate']")
        elem.click()
        time.sleep(1)
        elem = self.driver.find_element("xpath", "//input[@id='Trips_0__DepartDate']")
        elem.send_keys(day_after_next_str)
        time.sleep(0.5)

        elem = self.driver.find_element("xpath", '//label[@for="AwardCabinType_awardBusinessFirst"]')
        elem.click()
        time.sleep(0.5)

        elem = self.driver.find_element("xpath", '//button[@id="btn-search"]')
        elem.click()

        #self.driver.get(f"https://www.united.com/ual/en/us/flight-search/book-a-flight/results/awd?f=EWR&t=ORD&d={day_after_next_str}&tt=1&st=bestmatches&at=1&rm=1&act=2&cbm=-1&cbm2=-1&sc=7&px=1&taxng=1&idx=1")
        wait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, "//form[@id='flightSearch']")))
        time.sleep(1)


if __name__ == "__main__":
    session = SessionManager()
    session.login()
    print(session.driver.current_url)
