from pydantic import BaseModel
from typing import List, Optional, Dict
#from pydantic_computed import Computed, computed


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
    availability: str
    seat_remaining: str


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

    def __hash__(self):
        return hash((self.origin, self.destination, self.departure_time, self.arrival_time, self.travel_time))

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return NotImplemented

        return (
                self.origin == other.origin and
                self.destination == other.destination and
                self.departure_time == other.departure_time and
                self.arrival_time == other.arrival_time and
                self.travel_time == other.travel_time
        )

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
                text += f"{s.origin}-{s.destination}"
            else:
                previous_connection = \
                    f"({self.format_hour_minutes(s.connection_time)})" if s.connection_time > 0 else ""
                if last_segment_destination == s.origin:
                    text += f"{previous_connection}-{s.destination}"
                else:
                    text += f" {previous_connection} {s.origin}-{s.destination}"
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
            "engine": "UA",
            "origin": self.origin,
            "destination": self.destination,
            "stops": self.stops,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "duration": self.format_hour_minutes(self.travel_time),
            "flight_number": self.full_flight_number(),
            "aircraft": self.full_aircraft(),
            "routes": self.full_routes(),
            "miles": self.miles,
            "product_type": self.cabin,
            "all_cabin": self.full_cabin()
        }
