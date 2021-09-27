from pydantic import BaseModel
from typing import List


class Utility_Provider(BaseModel):
    street_address: str
    city: str
    state: str
    utility_provider_id: str


class Ven(BaseModel):
    id: str
    name: str
    registration_id: str
    finger_print: str
    utility_provider: Utility_Provider


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
        self.storage[ven.id] = ven

    def remove_ven(self, id: str):
        try:
            del self.storage[id]
        except KeyError as error:
            raise self.NotFound(str(error))

    def update_ven(self, id: str, ven: Ven):
        self.remove_ven(id)
        self.add_ven(ven)


    def find_ven(self, id: str):
        try:
            return self.storage[id]
        except KeyError as error:
            raise self.NotFound(str(error))

    def list_vens(self):
        return list(self.storage.values())
