from pydantic import BaseModel
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
        self.storage = {}

    def add_ven(self, ven: Ven):
        self.storage[ven.ven_name] = ven

    def remove_ven(self, ven_name: str):
        try:
            del self.storage[ven_name]
        except KeyError as error:
            raise self.NotFound(str(error))

    def update_ven(self, ven_name: str, ven: Ven):
        self.remove_ven(ven_name)
        self.add_ven(ven)

    def find_ven(self, ven_name: str):
        try:
            return self.storage[ven_name]
        except KeyError as error:
            raise self.NotFound(str(error))

    def list_vens(self):
        return list(self.storage.values())
