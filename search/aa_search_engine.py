from american_airlines import AmericanAirlines
from american_airlines.parse import process_lowest_award_date
from proxy.proxy import Proxy

from typing import Literal
from datetime import datetime, date

class AASearchEngine(AmericanAirlines):
    def __init__(self):
        super().__init__()
        self.proxy = Proxy()

    def monthly_calendar_search(self,
                                origin: str,
                                destination: str,
                                year: str,
                                month: str,
                                cabin: str = Literal["COACH", "PREMIUM_COACH", "BUSINESS,FIRST", "FIRST", ""],
                                max_stops: Literal[None, "0", "1", "2"] = None
                                ):
        format_date = f"{year}-{month}-01"
        input_date = datetime.strptime(format_date, "%Y-%m-%d").date()
        today_date = date.today()
        input_date = today_date if input_date < today_date else input_date
        processed_date_string = input_date.strftime("%Y-%m-%d")
        response = self.calendar_search(processed_date_string, origin, destination, cabin, max_stops, self.proxy.proxy_ip)
        print(response)
        result = process_lowest_award_date(response.json(), cabin)
        return result