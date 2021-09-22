from typing import List, Optional, Union

from aiohttp import web

from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r201, r204, r404

from model import Error, Ven


class VenCollectionView(PydanticView):
    async def get(self, ven_name: Optional[str] = None) -> r200[List[Ven]]:
        """
        List all vens
        Status Codes:
            200: Successful operation


        No need for payload on GET
        """
        vens = self.request.app["model"].list_vens()
        return web.json_response(
            [ven.dict() for ven in vens if ven_name is None or ven_name == ven.ven_name]
        )

    async def post(self, ven: Ven) -> r201[Ven]:
        """
        Add a new ven to the store
        Status Codes:
            201: Successful operation

        {
            "ven_name": "asdf",
            "ven_id": "asdf",
            "registration_id": "afds",
            "utility_provder_info": {
            "street_address": "asdf",
            "city": "asf",
            "state": "asf",
            "utility_id": 44444
            }
        }	
	

        """
        self.request.app["model"].add_ven(ven)
        return web.json_response(ven.dict())


class VenItemView(PydanticView):
    async def get(self, ven_name: str, /) -> Union[r200[Ven], r404[Error]]:
        """
        Find a ven by ID

        Status Codes:
            200: Successful operation
            404: Ven not found
        """
        ven = self.request.app["model"].find_ven(ven_name)
        return web.json_response(ven.dict())

    async def put(self, ven_name: str, /, ven: Ven) -> r200[Ven]:
        """
        Update an existing object

        Status Codes:
            200: Successful operation
            404: Ven not found
        """
        self.request.app["model"].update_ven(ven_name, ven)
        return web.json_response(ven.dict())

    async def delete(self, ven_name: str, /) -> r204:
        """
        Deletes a ven

        http://23.92.28.66:8080/vens/asfd
        """
        self.request.app["model"].remove_ven(ven_name)
        return web.Response(status=204)






class EventCollectionView(PydanticView):
    async def get(self, event_id: Optional[str] = None) -> r200[List[event]]:
        """
        List all events
        Status Codes:
            200: Successful operation


        No need for payload on GET
        """
        events = self.request.app["model"].list_event()
        return web.json_response(
            [event.dict() for event in events if event_id is None or event_id == event.event_id]
        )

    async def post(self, event: event) -> r201[event]:
        """
        Add a new event to the store
        Status Codes:
            201: Successful operation

        """
        self.request.app["model"].add_ven(event)
        return web.json_response(event.dict())


class EventItemView(PydanticView):
    async def get(self, event_id: str, /) -> Union[r200[event], r404[Error]]:
        """
        Status Codes:
            200: Successful operation
            404: event not found
        """
        event = self.request.app["model"].find_event(event_id)
        return web.json_response(event.dict())

    async def put(self, event_id: str, /, event: event) -> r200[event]:
        """
        Status Codes:
            200: Successful operation
            404: event not found
        """
        self.request.app["model"].update_event(event_id, event)
        return web.json_response(event.dict())

    async def delete(self, event_id: str, /) -> r204:
        """
        Deletes an event

        """
        self.request.app["model"].remove_event(event_id)
        return web.Response(status=204)