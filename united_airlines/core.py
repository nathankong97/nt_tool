import requests
from seleniumwire.utils import decode
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from .auth import SessionManager
from .config import UnitedAirlinesConfig
from .endpoints import CALENDAR_PRICING_API, CALENDAR_SEARCH_API, FLIGHT_SEARCH_API
from util.util import timing
from proxy.proxy import Proxy

import json
import time
from datetime import datetime


class UnitedAirlines(SessionManager, UnitedAirlinesConfig):
    def __init__(self, proxy=None):
        self.proxy = proxy
        if self.proxy:
            super().__init__(self.proxy.proxy_ip)
        else:
            super().__init__()

    def reset(self):
        self.proxy = Proxy()
        self.driver.quit()
        time.sleep(5)
        super().__init__(self.proxy.proxy_ip)

        self.get_token()
        print(self.key)

    def calendar_pricing(self,
                         departure_date: str,
                         origin: str,
                         destination: str,
                         ip: str = None) -> requests.Response:
        headers = self.HEADERS
        payload = self.CALENDAR_PRICING_PAYLOAD
        payload["Depart"] = departure_date
        payload["Origin"] = origin
        payload["Destination"] = destination
        payload["ClientCurrentDate"] = datetime.now().strftime('%Y-%m-%d')
        headers["X-Authorization-Api"] = self.key
        proxies = {'http': ip} if ip else None
        if proxies:
            r = self.session.post(CALENDAR_PRICING_API, headers=headers, json=payload, proxies=proxies)
        else:
            r = self.session.post(CALENDAR_PRICING_API, headers=headers, json=payload)
        return r

    @timing
    def calendar_search(self,
                        departure_date: str,
                        origin: str,
                        destination: str,
                        ip: str = None) -> requests.Response:
        # self.driver.get(self.CALENDAR_API_REFERER.format(origin, destination, departure_date))
        headers = self.HEADERS
        headers["Accept-Language"] = "en-US"
        headers["Content-Type"] = "application/json"
        headers["X-Authorization-Api"] = self.key
        headers["Referer"] = self.CALENDAR_API_REFERER.format(origin, destination, departure_date)
        print(headers["Referer"])
        with open("./united_airlines/payload.json") as f:
            payload = json.load(f)
            payload["Trips"][0]["Origin"] = origin
            payload["Trips"][0]["Destination"] = destination
            payload["Trips"][0]["DepartDate"] = departure_date
            parsed_date = datetime.strptime(departure_date, "%Y-%m-%d")
            formatted_date = parsed_date.strftime("%m/%d/%Y")
            search_key = f"{origin}{destination}{formatted_date}"
            payload["RecentSearchKey"] = search_key
        json_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        proxies = {'http': ip} if ip else None
        print("proxy ip: ", proxies)
        if proxies:
            r = self.session.post(CALENDAR_SEARCH_API, headers=headers, data=json_payload, proxies=proxies, timeout=45)
        else:
            r = self.session.post(CALENDAR_SEARCH_API, headers=headers, data=json_payload, timeout=45)
        return r

    # Expire since 11/14/2023, possibly of request header and payload change
    @timing
    def search(self,
               departure_date: str,
               origin: str,
               destination: str,
               ip: str = None) -> requests.Response:
        count = 0
        while count < 12:
            try:
                headers = self.HEADERS
                headers["Accept-Language"] = "en-US"
                headers["Content-Type"] = "application/json"
                headers["X-Authorization-Api"] = self.key
                headers["Referer"] = self.FLIGHT_API_REFERER.format(origin, destination, departure_date)
                headers["sec-fetch-dest"] = "empty"
                headers["sec-fetch-mode"] = "cors"
                headers["sec-fetch-site"] = "same-origin"
                with open("./united_airlines/flight_search_payload.json") as f:
                    payload = json.load(f)
                    payload["Trips"][0]["Origin"] = origin
                    payload["Trips"][0]["Destination"] = destination
                    payload["Trips"][0]["DepartDate"] = departure_date
                    parsed_date = datetime.strptime(departure_date, "%Y-%m-%d")
                    formatted_date = parsed_date.strftime("%m/%d/%Y")
                    search_key = f"{origin}{destination}{formatted_date}"
                    payload["RecentSearchKey"] = search_key
                json_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                proxies = {'http': self.proxy.proxy_ip} if ip else None
                print("proxy ip: ", proxies)
                if proxies:
                    r = self.session.post(FLIGHT_SEARCH_API, headers=headers, data=json_payload, proxies=proxies, timeout=15)
                else:
                    r = self.session.post(FLIGHT_SEARCH_API, headers=headers, data=json_payload, timeout=15)
                return r
            except Exception as e:
                count += 1
                print(e)
                print("Reset")
                self.reset()
        else:
            headers = self.HEADERS
            headers["Accept-Language"] = "en-US"
            headers["Content-Type"] = "application/json"
            headers["X-Authorization-Api"] = self.key
            headers["Referer"] = self.FLIGHT_API_REFERER.format(origin, destination, departure_date)
            headers["sec-fetch-dest"] = "empty"
            headers["sec-fetch-mode"] = "cors"
            headers["sec-fetch-site"] = "same-origin"
            with open("./united_airlines/flight_search_payload.json") as f:
                payload = json.load(f)
                payload["Trips"][0]["Origin"] = origin
                payload["Trips"][0]["Destination"] = destination
                payload["Trips"][0]["DepartDate"] = departure_date
                parsed_date = datetime.strptime(departure_date, "%Y-%m-%d")
                formatted_date = parsed_date.strftime("%m/%d/%Y")
                search_key = f"{origin}{destination}{formatted_date}"
                payload["RecentSearchKey"] = search_key
            json_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            r = self.session.post(FLIGHT_SEARCH_API, headers=headers, data=json_payload, timeout=15)
            return r

    @timing
    def search2(self,
                origin: str,
                destination: str,
                departure_date: str,
                ip: str = None,
                retry_time: int = 5
                ) -> requests.Response:
        count = 0
        while count < retry_time:
            try:
                headers = self.NEW_HEADER
                headers["referer"] = self.FLIGHT_API_REFERER.format(origin, destination, departure_date)
                headers["X-Authorization-Api"] = self.key
                with open("./united_airlines/flight_search_payload_new.json") as f:
                    payload = json.load(f)
                    payload["Trips"][0]["Origin"] = origin
                    payload["Trips"][0]["Destination"] = destination
                    payload["Trips"][0]["DepartDate"] = departure_date
                    parsed_date = datetime.strptime(departure_date, "%Y-%m-%d")
                    formatted_date = parsed_date.strftime("%m/%d/%Y")
                    search_key = f"{origin}{destination}{formatted_date}"
                    payload["RecentSearchKey"] = search_key
                    proxies = {'http': ip} if ip else None
                json_payload = json.dumps(payload, ensure_ascii=False).encode("utf-8")
                if ip:
                    r = self.session.post(
                        FLIGHT_SEARCH_API, headers=headers, data=json_payload, proxies=proxies, timeout=15)
                else:
                    r = self.session.post(FLIGHT_SEARCH_API, headers=headers, data=json_payload, timeout=15)
                return r
            except Exception as e:
                count += 1
                print(e)
                print("Reset")
                self.reset()

    @timing
    def web_search(self,
                   departure_date: str,
                   origin: str,
                   destination: str
                   ):
        time.sleep(1)
        page_url = self.FLIGHT_API_REFERER.format(origin, destination, departure_date)
        self.driver.get(page_url)

        """
        try:
            wait(self.driver, 30).until(EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'compareFaresLink')]")))
        except NoSuchElementException or TimeoutException:
            self.driver.save_screenshot('error1.png')
            try:
                wait(self.driver, 30).until(EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'NoFlights-styles__header')]")))
            except NoSuchElementException or TimeoutException:
                self.driver.save_screenshot('error2.png')"""

        #self.driver.save_screenshot('screenshot.png')
        request = self.driver.wait_for_request(FLIGHT_SEARCH_API, timeout=45)
        #result = [i for i in self.driver.requests if i.url == FLIGHT_SEARCH_API]
        response = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
        return response


if __name__ == "__main__":
    pass
