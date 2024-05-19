from .config import AmericanAirlinesConfig
from .endpoints import FLIGHT_ITINERARY_API, CALENDAR_SEARCH_API
from .parse import process_lowest_award_date, process_lowest_award_itinerary, filter_unique_routes
from .search import itinerary_api_search
from .model import ResponseSlice, Itinerary

import requests
import json
from typing import Literal, List, Dict
from datetime import datetime, timedelta
from util.util import export_to_csv


class AmericanAirlines(AmericanAirlinesConfig):
    def __init__(self):
        self.session = requests.Session()

    def search(self,
               departure_date: str,
               origin: str,
               destination: str,
               cabin: Literal["COACH", "PREMIUM_ECONOMY", "BUSINESS,FIRST", "FIRST", ""]
               ) -> List[Itinerary]:
        headers = self.HEADERS
        payload = self.ITINERARY_PAYLOAD
        payload["slices"][0]["departureDate"] = departure_date
        payload["slices"][0]["origin"] = origin
        payload["slices"][0]["destination"] = destination
        payload["slices"][0]["cabin"] = cabin
        payload["tripOptions"]["searchType"] = "Award"
        r = itinerary_api_search(self.session, headers, payload)
        data = r.json()
        response_slice = ResponseSlice()
        response_slice.slices = data["slices"]
        itineraries = response_slice.process_award_itinerary("lowest", cabin)
        return itineraries

    def pricing_search(self,
                       departure_date: str,
                       origin: str,
                       destination: str) -> Dict:
        headers = self.HEADERS
        payload = self.ITINERARY_PAYLOAD
        payload["slices"][0]["departureDate"] = departure_date
        payload["slices"][0]["origin"] = origin
        payload["slices"][0]["destination"] = destination
        payload["tripOptions"]["searchType"] = "Revenue"
        r = itinerary_api_search(self.session, headers, payload)
        data = r.json()

        return data

    def calendar_search(self,
                        departure_date: str,
                        origin: str,
                        destination: str,
                        cabin: str = "",
                        max_stops: Literal[None, "0", "1", "2"] = None,
                        ip: str = None
                        ) -> requests.Response:
        headers = self.HEADERS
        payload = self.ITINERARY_PAYLOAD
        payload["slices"][0]["departureDate"] = departure_date
        payload["slices"][0]["origin"] = origin
        payload["slices"][0]["destination"] = destination
        payload["slices"][0]["cabin"] = cabin
        payload["slices"][0]["maxStops"] = max_stops if max_stops else payload["slices"][0]["maxStops"]
        proxies = {'http': ip} if ip else None
        if proxies:
            r = self.session.post(CALENDAR_SEARCH_API, headers=headers, json=payload, proxies=proxies)
        else:
            r = self.session.post(CALENDAR_SEARCH_API, headers=headers, json=payload)
        return r

    def premium_search(self, origin: str, destination: str) -> List[Dict]:
        cabin = "BUSINESS,FIRST"
        origin = origin
        destination = destination
        all_dates = []

        current_date = datetime.now() + timedelta(days=1)
        response = self.calendar_search(current_date.strftime('%Y-%m-%d'), origin, destination, cabin)
        month_dates = process_lowest_award_date(response.json(), cabin)
        all_dates.extend(month_dates)

        for _ in range(5):
            next_month = current_date.month + 1 if current_date.month < 12 else 1
            next_year = current_date.year + 1 if current_date.month == 12 else current_date.year
            current_date = current_date.replace(year=next_year, month=next_month, day=1)
            response = self.calendar_search(current_date.strftime('%Y-%m-%d'), origin, destination, cabin)
            month_dates = process_lowest_award_date(response.json(), cabin)
            all_dates.extend(month_dates)

        print(all_dates)

        results = []
        for date in all_dates:
            response = self.search(date, origin, destination, cabin)
            results.extend(response)

        all_segments = filter_unique_routes(results)
        all_segments = [s.to_dict() for s in all_segments]
        return all_segments


if __name__ == "__main__":
    aa = AmericanAirlines()
    result = aa.calendar_search(
        "2023-09-12",
        "ORD",
        "TYO"
    )
