try:
    from typing import Dict, Literal, List
except:
    from typing_extensions import Literal
    from typing import Dict, List
from datetime import datetime
import re

from .ticket_config import PRODUCT_TYPE, ASIA_AMERICA_MILES_THRESHOLD
from .model import Segment, Itinerary
from db import Airport, session
from sqlalchemy import select


def process_lowest_award_date(response: Dict,
                              cabin: Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST", ""]
                              ) -> List[Dict]:
    cabin = "ECONOMY" if cabin == "" else cabin
    all_dates = []
    weeks = response["data"]["Calendar"]["Months"][0]["Weeks"]
    for week in weeks:
        days = week["Days"]
        for day in days:
            d = {}
            if day["Solutions"]:
                for solution in day["Solutions"]:
                    product_type = PRODUCT_TYPE[solution["CabinType"]]
                    if product_type == cabin:
                        tax = [p["Amount"] for p in solution["Prices"] if p["PricingType"] == "Tax"][0]
                        miles = [p["Amount"] for p in solution["Prices"] if p["PricingType"] == "Award"][0]
                        low_miles = miles <= ASIA_AMERICA_MILES_THRESHOLD[product_type]
                        if low_miles:
                            format_date = datetime.strptime(day["DateValue"], "%m/%d/%Y").strftime("%Y-%m-%d")
                            d[format_date] = {
                                "miles": miles,
                                "tax": tax
                            }
                            all_dates.append(d)
    cleaned_dates = process_ghost_ticket(all_dates)
    return cleaned_dates

def process_ghost_ticket(award_list: List[Dict]):
    # This is to clean up BR Ghost Ticket -> Tax always == $21.1
    for d in award_list[:]:
        if list(d.values())[0]["tax"] == 21.1:
            award_list.remove(d)
    return award_list


def process_lowest_award_itinerary(response: Dict,
                                   cabin: Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST", ""]
                                   ) -> List[Itinerary]:
    cabin = "ECONOMY" if cabin == "" else cabin
    itineraries = []
    flights = response["data"]["Trips"][0]["Flights"]
    for flight in flights:
        itinerary = Itinerary(segments=[])
        current_lowest_mile = 0
        find_award_flight = False
        raw_product_type = None
        products = flight["Products"]
        avail_products = []
        for product in products:
            product_type = PRODUCT_TYPE[product["ProductType"]]
            for price in product["Prices"]:
                award = price["PricingType"] == "Award"
                low_miles = price["Amount"] <= ASIA_AMERICA_MILES_THRESHOLD[product_type]
                if award and low_miles and product_type == cabin:
                    avail_products.append(product)
        if avail_products:
            avail_products = avail_products[0]
            raw_product_type = avail_products["ProductType"]
            booking_class = avail_products["BookingClassAvailability"]
            pattern = f'{avail_products["BookingCode"]}[0-9]+'
            match = re.search(pattern, booking_class)
            seat_result = match.group(0) if match else "0"
            find_award_flight = True
            segment = Segment(
                carrier=flight["OperatingCarrier"],
                flight_number=flight["OriginalFlightNumber"],
                aircraft=flight["EquipmentDisclosures"]["EquipmentType"],
                origin=flight["Origin"],
                destination=flight["Destination"],
                departure_time=flight["FlightInfo"]["ScheduledDepartureDateTime"],
                arrival_time=flight["FlightInfo"]["ScheduledArrivalDateTime"],
                duration=flight["TravelMinutes"],
                connection_time=0,
                cabin=avail_products["CabinType"],
                booking_code=avail_products["BookingCode"],
                availability=avail_products["BookingClassAvailability"],
                seat_remaining=seat_result
            )
            itinerary.segments.append(segment)
        if flight["Connections"] and find_award_flight:
            for connection in flight["Connections"]:
                product = [p for p in connection["Products"] if p["ProductType"] == raw_product_type][0]
                booking_class = product["BookingClassAvailability"]
                pattern = f'{product["BookingCode"]}[0-9]+'
                match = re.search(pattern, booking_class)
                seat_result = match.group(0) if match else "0"
                segment = Segment(
                    carrier=connection["OperatingCarrier"],
                    flight_number=connection["OriginalFlightNumber"],
                    aircraft=connection["EquipmentDisclosures"]["EquipmentType"],
                    origin=connection["Origin"],
                    destination=connection["Destination"],
                    departure_time=connection["FlightInfo"]["ScheduledDepartureDateTime"],
                    arrival_time=connection["FlightInfo"]["ScheduledArrivalDateTime"],
                    duration=connection["TravelMinutes"],
                    connection_time=connection["ConnectTimeMinutes"],
                    cabin=product["CabinType"],
                    booking_code=product["BookingCode"],
                    availability=product["BookingClassAvailability"],
                    seat_remaining=seat_result
                )
                itinerary.segments.append(segment)
        if itinerary.segments:
            itinerary.origin = itinerary.segments[0].origin
            itinerary.destination = itinerary.segments[-1].destination
            itinerary.departure_time = itinerary.segments[0].departure_time
            itinerary.arrival_time = itinerary.segments[-1].arrival_time
            itinerary.stops = len(itinerary.segments) - 1
            itinerary.travel_time = flight["TravelMinutesTotal"]
            itinerary.miles = [p["Amount"] for p in avail_products["Prices"] if p["PricingType"] == "Award"][0]
            itinerary.cabin = cabin
            itineraries.append(itinerary)
    return itineraries


def filter_unique_routes(itineraries: List[Itinerary]) -> List[Itinerary]:
    new_itineraries = []

    for itinerary in itineraries:
        origin_country = session.scalar(select(Airport).where(Airport.iata == itinerary.segments[0].origin)).country
        for segment in itinerary.segments[:]:
            dest_country = session.scalar(select(Airport).where(Airport.iata == segment.destination)).country
            if origin_country == dest_country:
                itinerary.segments.remove(segment)
        itinerary.segments[0].connection_time = 0
        itinerary.origin = itinerary.segments[0].origin
        itinerary.departure_time = itinerary.segments[0].departure_time
        itinerary.stops = len(itinerary.segments) - 1
        itinerary.travel_time = sum([s.duration for s in itinerary.segments]) + sum(
            [s.connection_time for s in itinerary.segments])
        new_itineraries.append(itinerary)
    unique_itineraries = list(set(new_itineraries))
    return unique_itineraries
