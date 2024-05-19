from search import AASearchEngine
from american_airlines.parse import process_all_pricing_itinerary, process_lowest_award_date
from united_airlines import UnitedAirlines
from united_airlines.parse import process_lowest_award_itinerary, process_lowest_award_date
from proxy.proxy import Proxy

import sys
# sys.path.append("/root/pi/Stock-Trading-System")

# from tools.util import prepare_email_attachment_content, send_email
from datetime import datetime
import pandas as pd
import json

# aa = AASearchEngine()
proxy = Proxy()

#result = aa.monthly_calendar_search("LAX", "HKG", "2023", "10", "BUSINESS,FIRST")
#print(result)


ua = UnitedAirlines(proxy)
ua.get_token()
print(ua.key)
print(ua.proxy)

result = ua.calendar_search("2023-10-24", "NYC", "TYO", proxy.proxy_ip)
print(process_lowest_award_date(result.json(), "BUSINESS"))

result = ua.search("2023-10-28", "JFK", "HND")
flights = process_lowest_award_itinerary(result.json(), "BUSINESS")
segments = []
for f in flights:
    for s in f.segments:
        segments.append(s)

df = pd.DataFrame([i.__dict__ for i in segments])
df.drop("connection_time", axis=1, inplace=True)
filtered_df = df[(df["booking_code"].isin(("I", "IN"))) & (df["duration"] > 400)]
filtered_df = filtered_df.drop_duplicates()
filtered_df["seat_count"] = filtered_df["seat_remaining"].apply(lambda x: x[-1])
data = []
for i, row in filtered_df.iterrows():
    d = {}
    datetime_id = datetime.strptime(row["departure_time"], "%Y-%m-%d %H:%M").strftime("%Y%m%d")
    flight_id = f"{datetime_id}-{row['carrier'].lower()}{row['flight_number']}-{row['origin'].lower()}-{row['destination'].lower()}"
    d["flight_id"] = flight_id
    d["origin"] = row["origin"]
    d["destination"] = row["destination"]
    d["aircraft"] = row["aircraft"]
    d["duration"] = row["duration"]
    d["first_seen"] = datetime.now().isoformat()
    d["last_seen"] = []
    last_seen = {
        "timestamp": datetime.now().isoformat(),
        "status": "available",
        "class": row["cabin"],
        "code": row["booking_code"],
        "seats_remaining": row["seat_count"]
    }
    d["last_seen"].append(last_seen)
    data.append(d)

#result = aa.premium_search("TYO", "PVG")
#print(result)
#ua = UnitedAirlines()
#ua.get_token()
#ua.login()
#result = ua.web_search("2023-10-19", "EWR", "SFO")

# dates = process_lowest_award_date(response.json(), "BUSINESS")
# print(dates)
# result = ua.web_search("2023-09-19", "EWR", "HKG")
