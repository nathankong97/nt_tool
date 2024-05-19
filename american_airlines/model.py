from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime

from .ticket_config import ASIA_AMERICA_MILES_THRESHOLD


class Segment(BaseModel):
    carrier: str
    flight_number: str
    aircraft: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: int
    connection_time: int
    cabin: str
    booking_code: str

    def __hash__(self):
        return hash((self.carrier, self.flight_number, self.origin, self.destination, self.departure_time, self.cabin))

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented

        return (
                self.carrier == other.carrier and
                self.flight_number == other.flight_number and
                self.origin == other.origin and
                self.destination == other.destination and
                self.departure_time == other.departure_time and
                self.cabin == other.cabin
        )

    def to_dict(self):
        return self.__dict__


class Itinerary(BaseModel):
    segments: List[Segment]
    origin: Optional[str]
    destination: Optional[str]
    departure_time: Optional[str]
    arrival_time: Optional[str]
    stops: Optional[int]
    travel_time: Optional[int]
    miles: Optional[int]
    cabin: Optional[str]

    @staticmethod
    def format_datetime(input_datetime: str) -> str:
        parsed_datetime = datetime.strptime(input_datetime, "%Y-%m-%dT%H:%M:%S.%f%z")
        formatted_datetime = parsed_datetime.strftime("%Y-%m-%d %H:%M")
        return formatted_datetime

    @staticmethod
    def format_hour_minutes(minutes: int):
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if hours == 0:
            return f"{remaining_minutes}min"
        elif remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h{remaining_minutes}min"

    def full_flight_number(self) -> str:
        text = ""
        for s in self.segments:
            flight_number = f"{s.carrier}{s.flight_number}-"
            text += flight_number
        if text[-1] == "-":
            text = text[:-1]
        return text

    def full_aircraft(self) -> str:
        text = ""
        for s in self.segments:
            aircraft = f"{s.aircraft}-"
            text += aircraft
        if text[-1] == "-":
            text = text[:-1]
        return text

    def full_routes(self):
        text = ""
        last_segment_destination = ""

        if len(self.segments) == 1:
            return f"{self.origin}-{self.destination}"
        for i, s in enumerate(self.segments):
            if i == 0:
                text += f"{s.origin}-{s.destination}({self.format_hour_minutes(s.connection_time)})"
            else:
                after_connection = f"({self.format_hour_minutes(s.connection_time)})" if s.connection_time > 0 else ""
                if last_segment_destination == s.origin:
                    text += f"-{s.destination}{after_connection}"
                else:
                    text += f" {s.origin}-{s.destination}{after_connection}"
            last_segment_destination = s.destination
        return text

    def full_cabin(self):
        text = ""
        for s in self.segments:
            cabin = f"{s.cabin}-"
            text += cabin
        if text[-1] == "-":
            text = text[:-1]
        return text

    def to_dict(self) -> Dict:
        return {
            "engine": "AA",
            "origin": self.origin,
            "destination": self.destination,
            "stops": self.stops,
            "departure_time": self.format_datetime(self.departure_time),
            "arrival_time": self.format_datetime(self.arrival_time),
            "duration": self.format_hour_minutes(self.travel_time),
            "flight_number": self.full_flight_number(),
            "aircraft": self.full_aircraft(),
            "routes": self.full_routes(),
            "miles": self.miles,
            "product_type": self.cabin,
            "all_cabin": self.full_cabin()
        }


class PricingItinerary(Itinerary):
    price: Optional[float]
    flagship: Optional[bool]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.miles

    def to_dict(self) -> Dict:
        return {
            "engine": "AA",
            "origin": self.origin,
            "destination": self.destination,
            "stops": self.stops,
            "departure_time": self.format_datetime(self.departure_time),
            "arrival_time": self.format_datetime(self.arrival_time),
            "duration": self.format_hour_minutes(self.travel_time),
            "flight_number": self.full_flight_number(),
            "aircraft": self.full_aircraft(),
            "routes": self.full_routes(),
            "price": self.price,
            "product_type": self.cabin,
            "all_cabin": self.full_cabin(),
            "flagship": self.flagship
        }


class ResponseSlice(BaseModel):
    slices: Optional[List[Dict]]
    filter_method = ["all", "lowest"]

    def filter_condition(self, method: str, cabin: str = "", points: int = 0) -> bool:
        if method not in self.filter_method:
            raise Exception("Invalid filter method: ", method)
        if method == "all":
            return True
        elif method == "lowest":
            return points < ASIA_AMERICA_MILES_THRESHOLD[cabin]

    def _filter_cabin(self,
                      itineraries: List[Union[Itinerary, PricingItinerary]],
                      cabin: Literal["COACH", "PREMIUM_ECONOMY", "BUSINESS,FIRST", "FIRST", ""]
                      ) -> List[Union[Itinerary, PricingItinerary]]:
        new_list = []
        for i in itineraries:
            print(i.cabin, cabin, i.cabin in cabin)
            if i.cabin in cabin:
                new_list.append(i)
        return new_list

    def process_award_itinerary(self,
                                method: Literal["all", "lowest"],
                                cabin: Literal["COACH", "PREMIUM_ECONOMY", "BUSINESS,FIRST", "FIRST", ""]
                                ) -> List[Itinerary]:
        valid_cabin = "COACH" if cabin == "" else cabin
        itineraries = []
        for slice_index, s in enumerate(self.slices):
            pricing = [p for p in s["pricingDetail"] if p["perPassengerAwardPoints"] != 0]
            for i, p in enumerate(pricing):
                itinerary = Itinerary(segments=[])
                if self.filter_condition(method, valid_cabin, p["perPassengerAwardPoints"]):
                    for segment in s["segments"]:
                        if len(segment["legs"][0]["productDetails"]) == 1:
                            valid_cabin = segment["legs"][0]["productDetails"][i]["cabinType"]
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
        if method == "lowest":
            itineraries = self._filter_cabin(itineraries, cabin)
        return itineraries
