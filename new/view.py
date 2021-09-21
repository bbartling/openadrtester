from typing import List, Optional, Union

from aiohttp import web

from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r201, r204, r404

from model import Error, Ven


class VenCollectionView(PydanticView):
    async def get(self, age: Optional[str] = None) -> r200[List[Ven]]:
        """
        List all vens

        Status Codes:
            200: Successful operation
        """
        vens = self.request.app["model"].list_vens()
        return web.json_response(
            [ven.dict() for ven in vens if age is None or age == ven.age]
        )

    async def post(self, ven: Ven) -> r201[Ven]:
        """
        Add a new ven to the store

        Status Codes:
            201: Successful operation
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
        """
        self.request.app["model"].remove_ven(ven_name)
        return web.Response(status=204)
