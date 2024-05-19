from united_airlines import UnitedAirlines
from united_airlines.parse import process_lowest_award_itinerary, process_lowest_award_date
from proxy.proxy import Proxy
from db.mongo import MongoDB
from subscription import TelegramSubscription

from datetime import datetime, timedelta, time
from sqlalchemy import create_engine
import pandas as pd
import sys

print("Start IAH Searching")
#sys.stdout = open(f'/root/pi/nt_tool/united_award_tracking/{datetime.now()}.log', 'w')

# CLASS OBJECT INITIALIZATION
engine = create_engine("mysql://pi:aptx4869@localhost/flight_data")
mongo = MongoDB("united")
collection = mongo.db["award_ticket_tracking"]
proxy = Proxy()
ua = UnitedAirlines(proxy)
bot = TelegramSubscription()
fare_class = "BUSINESS"
date_format = "%Y-%m-%d"
ua.get_token()
print(ua.key)
print("UA Proxy:", ua.proxy)

# GET DATES TO SEARCH IN CALENDAR
current_date = datetime.now()
cutoff_time = time(18, 0)
if current_date.time() > cutoff_time:
    current_date += timedelta(days=1)
first_days = [current_date]
for _ in range(1):
    current_date = current_date.replace(day=1) + timedelta(days=32)
    first_days.append(current_date.replace(day=1))
formatted_dates = [date.strftime(date_format) for date in first_days]

# GET DATES CONTAINING LOWEST AWARD TICKET
lowest_award_dates = []
for date in formatted_dates:
    result = ua.calendar_search(date, "IAH", "TYO", proxy.proxy_ip)
    date_result = process_lowest_award_date(result.json(), fare_class)
    for sub_date in date_result:
        lowest_award_dates.append(sub_date)

# REMOVE DUPLICATES IN LIST OF DICTIONARIES
seen = set()
lowest_award_dates = [entry for entry in lowest_award_dates if not (
        str(entry) in seen or seen.add(str(entry)))]
print("IAH Result", lowest_award_dates)


# SEARCH LIST OF LOWEST AWARD TICKETS IN SPECIFIC DATES
date_keys = [next(iter(entry)) for entry in lowest_award_dates]
segments = []
for date in date_keys:
    result = ua.search2("IAH", "HND", date, proxy.proxy_ip)
    flights = process_lowest_award_itinerary(result.json(), fare_class)
    for f in flights:
        for s in f.segments:
            segments.append(s)

# USE PANDAS FOR ADVANCED DATA CLEANING
df = pd.DataFrame([i.__dict__ for i in segments])
df.drop("connection_time", axis=1, inplace=True)
filtered_df = df[(df["booking_code"].isin(("I", "IN"))) & (df["duration"] > 400)]
filtered_df = filtered_df.drop_duplicates(
    subset=["carrier", "flight_number", "origin", "destination", "departure_time"], keep="last")
filtered_df["seat_count"] = filtered_df["seat_remaining"].apply(
    lambda x: x[-1])
print(filtered_df)

# SEND SUBSCRIPTION DATA
new_flights = []
non_exist_flights = []
query = "SELECT flight_id FROM temp_united_award"
temp_united_award_df = pd.read_sql(query, con=engine)
old_ids = [i[:-1] for i in temp_united_award_df["flight_id"].to_list()]
subscription_df = filtered_df[filtered_df["carrier"].str.contains('UA|NH')]
subscription_df["flight_id"] = subscription_df['carrier'] + subscription_df['flight_number'] + '-' + \
                               subscription_df['origin'] + \
                               '-' + subscription_df['destination'] + '-' + \
                               subscription_df['departure_time'] + ' ' + \
                               subscription_df['seat_remaining']
new_ids = subscription_df["flight_id"].to_list()
new_ids_without_seat = [i[:-1] for i in new_ids]
for new_id in new_ids:
    if new_id[:-1] not in old_ids:
        new_flights.append(new_id)
for old_id in old_ids:
    if old_id not in new_ids_without_seat:
        non_exist_flights.append(old_id[:-1])

new_flight_pre_message = "New Flight Found!\n"
new_flight_message = "\n".join(new_flights)
non_flight_pre_message = "\nFlights Not Available Anymore:\n"
non_flight_message = "\n".join(non_exist_flights)
new_flight_final_message = new_flight_pre_message + new_flight_message
non_flight_final_message = non_flight_pre_message + non_flight_message
if not new_flights:
    bot.send_message("No New Flight Found\n" + non_flight_final_message)
else:
    bot.send_message(new_flight_final_message + non_flight_final_message)

"""
subscription_df.to_sql('temp_united_award', con=engine, if_exists='replace', index=False)
ids = subscription_df["flight_id"].to_list()
message = "\n".join(ids)
bot.send_message(message)

# STORE TARGETED DATA FORMAT INTO LIST OF DICTIONARIES
# THIS IS THE PREPARATION FOR MONGODB
final_data = []
latest_data_ids = []
for i, row in filtered_df.iterrows():
    d = {}
    datetime_id = datetime.strptime(
        row["departure_time"], "%Y-%m-%d %H:%M").strftime("%Y%m%d")
    flight_id = f"{datetime_id}-{row['carrier'].lower()}{row['flight_number']}-{row['origin'].lower()}-{row['destination'].lower()}"
    d["flight_id"] = flight_id
    d["carrier"] = row['carrier']
    d["origin"] = row["origin"]
    d["destination"] = row["destination"]
    d["aircraft"] = row["aircraft"]
    d["duration"] = row["duration"]
    d["departure_time"] = row["departure_time"]
    d["arrival_time"] = row["arrival_time"]
    d["first_seen"] = datetime.now().isoformat()
    d["last_seen"] = []
    last_seen = {
        "timestamp": datetime.now().isoformat(),
        "class": row["cabin"],
        "code": row["booking_code"],
        "seats_remaining": row["seat_count"],
        "status": "available",
        "fare_class": row["availability"]
    }
    d["last_seat_counts"] = last_seen["seats_remaining"]
    d["last_seen"].append(last_seen)
    final_data.append(d)
    latest_data_ids.append(flight_id)

# INSERT DATA INTO THE COLLECTION IF NEW; OR, UPDATE 'LAST_SEEN' ARRAY IF EXISTED
for entry in final_data:
    flight_id = entry["flight_id"]
    filter_result = collection.find_one({"flight_id": flight_id})
    if filter_result is None:
        x = collection.insert_one(entry)
        print(x.inserted_id)
    else:
        last_seen = entry["last_seen"][0]
        collection.update_one(
            {"flight_id": flight_id},
            {"$push": {"last_seen": last_seen}}
        )
        collection.update_one(
            {"flight_id": flight_id},
            {"$set": {
                "departure_time": entry["departure_time"],
                "arrival_time": entry["arrival_time"],
                "last_seat_counts": entry["last_seat_counts"]
            }
            }
        )
        updated_result = collection.find_one({"flight_id": flight_id})

# UPDATE STATUS TO UNAVAILABLE IF AWARD TICKET DISAPPEARED
current_mongo_entries = list(collection.find())
for entry in current_mongo_entries:
    flight_id = entry["flight_id"]
    try:
        flight_departure = entry["departure_time"]
        flight_departure = datetime.strptime(
            flight_departure, "%Y-%m-%d %H:%M")
        if flight_departure >= datetime.now() and flight_id not in latest_data_ids:
            last_seen = {
                "timestamp": datetime.now().isoformat(),
                "class": row["cabin"],
                "code": row["booking_code"],
                "seats_remaining": 0,
                "status": "unavailable",
                "fare_class": ""
            }
            collection.update_one(
                {"flight_id": flight_id},
                {"$push": {"last_seen": last_seen}}
            )
            collection.update_one(
                {"flight_id": flight_id},
                {"$set": {
                    "last_seat_counts": 0
                }
                }
            )
    except:
        pass

ua.driver.quit()"""



