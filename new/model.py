from pydantic import BaseModel
from datetime import datetime,timedelta
from typing import List


class Utility_Provder_Info(BaseModel):
    street_address: str
    city: str
    state: str
    utility_id: int


class Ven(BaseModel):
    ven_name: str
    ven_id: str
    registration_id: str
    utility_provder_info: Utility_Provder_Info


class Event_Intervals(BaseModel):
    dtstart: datetime
    duration: timedelta
    signal_payload: float


class Event(BaseModel):
    ven_id: str
    event_id: str
    event_intervals: List(Event_Intervals)


    '''
    OPEN LEADR CODE EXAMPLE FOR EVENT CREATION

    server.add_event(ven_id=ven_id,
        signal_name='LOAD_CONTROL',
        signal_type='x-loadControlCapacity',
        intervals=[{'dtstart': event_start_utc,
                    'duration': timedelta(minutes=minutes),
                    'signal_payload': 1.0}],
        callback=event_response_callback,
        event_id=event_start_formatted_local_tz,
    )
    '''



class Error(BaseModel):
    error: str


class Model:
    """
    To keep simple this demo, we use a simple dict as database to
    store the models.
    """

    class NotFound(KeyError):
        """
        Raised when a ven is not found.
        """

    def __init__(self):
        self.ven_storage = {}
        self.event_storage = {}


    def add_ven(self, ven: Ven):
        self.ven_storage[ven.ven_name] = ven


    def add_event(self, event: Event):
        self.event_storage[event.event_name] = event


    def remove_ven(self, ven_name: str):
        try:
            del self.ven_storage[ven_name]
        except KeyError as error:
            raise self.NotFound(str(error))


    def remove_event(self, event_name: str):
        try:
            del self.event_storage[event_name]
        except KeyError as error:
            raise self.NotFound(str(error))


    def update_ven(self, ven_name: str, ven: Ven):
        self.remove_ven(ven_name)
        self.add_ven(ven)


    def update_event(self, event_name: str, event: Event):
        self.remove_event(event_name)
        self.add_event(event)


    def find_ven(self, ven_name: str):
        try:
            return self.ven_storage[ven_name]
        except KeyError as error:
            raise self.NotFound(str(error))


    def find_event(self, event_name: str):
        try:
            return self.event_storage[event_name]
        except KeyError as error:
            raise self.NotFound(str(error))


    def list_vens(self):
        return list(self.ven_storage.values())


    def list_events(self):
        return list(self.event_storage.values())