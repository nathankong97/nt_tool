from .ticket_config import ASIA_AMERICA_MILES_THRESHOLD, FARE_CHART
from .model import Itinerary, Segment, PricingItinerary
from db import Airport, session
from sqlalchemy import select

from typing import List, Dict, Literal


def process_lowest_award_date(response: Dict,
                              cabin: Literal["COACH", "PREMIUM_COACH", "BUSINESS,FIRST", "FIRST", ""]
                              ) -> List[str]:
    print(response.keys())
    if response["error"] == "309":
        return []
    cabin = "COACH" if cabin == "" else cabin
    origin = response["calendarDetails"]["calendarSliceTabs"][0]["origin"]
    destination = response["calendarDetails"]["calendarSliceTabs"][0]["destination"]
    o_country = session.scalar(select(Airport).where(Airport.iata == origin)).country
    d_country = session.scalar(select(Airport).where(Airport.iata == destination)).country
    asian_countries = ["Hong Kong", "China", "Japan", "South Korea"]
    if any(country for country in (o_country, d_country) if country in asian_countries):
        fare_chart = FARE_CHART["ASIA"]
    else:
        fare_chart = FARE_CHART["USA"]
    return [
        day["date"]
        for month in response["calendarMonths"]
        for week in month["weeks"]
        for day in week["days"]
        if day["date"] and
           day["solution"] and
           day["solution"]["perPassengerAwardPoints"] < fare_chart[cabin]
    ]


def process_lowest_award_itinerary(response: Dict,
                                   cabin: Literal["COACH", "PREMIUM_ECONOMY", "BUSINESS,FIRST", "FIRST", ""]
                                   ) -> List[Itinerary]:
    cabin = "COACH" if cabin == "" else cabin
    itineraries = []
    slices = response["slices"]
    for slice_index, s in enumerate(slices):
        pricing = [p for p in s["pricingDetail"] if p["perPassengerAwardPoints"] != 0]
        for i, p in enumerate(pricing):
            itinerary = Itinerary(segments=[])
            if p["perPassengerAwardPoints"] < ASIA_AMERICA_MILES_THRESHOLD[cabin]:
                for segment in s["segments"]:
                    if len(segment["legs"][0]["productDetails"]) == 1:
                        cabin = segment["legs"][0]["productDetails"][i]["cabinType"]
                    segment_object = Segment(
                        carrier=segment["flight"]["carrierCode"],
                        flight_number=segment["flight"]["flightNumber"],
                        aircraft=segment["legs"][0]["aircraftCode"],
                        origin=segment["legs"][0]["origin"]["code"],
                        destination=segment["legs"][0]["destination"]["code"],
                        departure_time=segment["legs"][0]["departureDateTime"],
                        arrival_time=segment["legs"][0]["arrivalDateTime"],
                        duration=segment["legs"][0]["durationInMinutes"],
                        connection_time=segment["legs"][0]["connectionTimeInMinutes"],
                        cabin=segment["legs"][0]["productDetails"][i]["cabinType"],
                        booking_code=segment["legs"][0]["productDetails"][i]["bookingCode"]
                    )
                    itinerary.segments.append(segment_object)
                if itinerary.segments:
                    itinerary.origin = s["origin"]["code"]
                    itinerary.destination = s["destination"]["code"]
                    itinerary.departure_time = s["departureDateTime"]
                    itinerary.arrival_time = s["arrivalDateTime"]
                    itinerary.stops = s["stops"]
                    itinerary.travel_time = s["durationInMinutes"]
                    itinerary.miles = p["perPassengerAwardPoints"]
                    itinerary.cabin = p["productType"]
                    itineraries.append(itinerary)
    return itineraries


def filter_unique_routes(itineraries: List[Itinerary]) -> List[Segment]:
    all_segments = []
    for itinerary in itineraries:
        segments = itinerary.segments
        for segment in segments:
            origin_country = session.scalar(select(Airport).where(Airport.iata == segment.origin)).country
            dest_country = session.scalar(select(Airport).where(Airport.iata == segment.destination)).country
            if origin_country != dest_country:
                all_segments.append(segment)

    unique_segments = list(set(all_segments))
    return unique_segments


def process_all_pricing_itinerary(response: Dict) -> List[PricingItinerary]:
    itineraries = []
    slices = response["slices"]
    for s in slices:
        for i, p in enumerate(s["productDetails"]):
            itinerary = PricingItinerary(segments=[])
            for segment in s["segments"]:
                segment_object = Segment(
                    carrier=segment["flight"]["carrierCode"],
                    flight_number=segment["flight"]["flightNumber"],
                    aircraft=segment["legs"][0]["aircraftCode"],
                    origin=segment["legs"][0]["origin"]["code"],
                    destination=segment["legs"][0]["destination"]["code"],
                    departure_time=segment["legs"][0]["departureDateTime"],
                    arrival_time=segment["legs"][0]["arrivalDateTime"],
                    duration=segment["legs"][0]["durationInMinutes"],
                    connection_time=segment["legs"][0]["connectionTimeInMinutes"],
                    cabin=segment["legs"][0]["productDetails"][i]["productType"],
                    booking_code=segment["legs"][0]["productDetails"][i]["bookingCode"]
                )
                itinerary.segments.append(segment_object)
            if itinerary.segments:
                price = [pri for pri in s["pricingDetail"] if pri["productType"] == p["productType"]][0][
                    "perPassengerDisplayTotal"]["amount"]
                itinerary.origin = s["origin"]["code"]
                itinerary.destination = s["destination"]["code"]
                itinerary.departure_time = s["departureDateTime"]
                itinerary.arrival_time = s["arrivalDateTime"]
                itinerary.stops = s["stops"]
                itinerary.travel_time = s["durationInMinutes"]
                itinerary.price = price
                itinerary.cabin = p["productType"]
                itinerary.flagship = p["flagship"]
                itineraries.append(itinerary)
    return itineraries
