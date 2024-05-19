from united_airlines import UnitedAirlines
from united_airlines.parse import process_lowest_award_itinerary, process_lowest_award_date
from proxy.proxy import Proxy

import telebot
import pandas as pd
import sys
from datetime import datetime


sys.stdout = open(f'/home/littlepink0505/nt_tools/united_award_tracking_20231208/{datetime.now()}.log', 'w')
bot = telebot.TeleBot("6679505950:AAH4JpkX3sUrabdyv_n36jkT7EOoMblcM7w")
proxy = Proxy()
ua = UnitedAirlines(proxy)
segments = []

ua.get_token()
print(ua.key)

airports = ["JFK", "IAD", "SFO", "IAH", "LAX"]
for airport in airports:
    result = ua.search2(airport, "HND", "2023-12-08", proxy.proxy_ip, 13)
    flights = process_lowest_award_itinerary(result.json(), "BUSINESS")
    for f in flights:
        for s in f.segments:
            segments.append(s)

df = pd.DataFrame([i.__dict__ for i in segments])
if not df.empty:
    df.drop("connection_time", axis=1, inplace=True)
    filtered_df = df[(df["booking_code"].isin(("I", "IN"))) & (df["duration"] > 400)]
    filtered_df = filtered_df.drop_duplicates(
        subset=["carrier", "flight_number", "origin", "destination", "departure_time"], keep="last")
    filtered_df["seat_count"] = filtered_df["seat_remaining"].apply(lambda x: x[-1])
    subscription_df = filtered_df[filtered_df["carrier"].str.contains('UA|NH')]
    subscription_df["flight_id"] = subscription_df['carrier'] + subscription_df['flight_number'] + '-' + \
                                   subscription_df['origin'] + \
                                   '-' + subscription_df['destination'] + '-' + \
                                   subscription_df['departure_time'] + ' ' + \
                                   subscription_df['seat_remaining']
    ids = subscription_df["flight_id"].to_list()
    message = "\n".join(ids)
    bot.send_message(1005006712, message)
    bot.send_message(5367739358, message)

    print(filtered_df)
else:
    bot.send_message(1005006712, "2023-12-08 No Flight Found.")
