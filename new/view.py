from typing import List, Optional, Union

from aiohttp import web

from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r201, r204, r404

from model import Error, Ven



class VenCollectionView(PydanticView):
    async def get(self, id: Optional[int] = None) -> r200[List[Ven]]:
        """
        List all vens

        Status Codes:
            200: Successful operation
        """
        vens = self.request.app["model"].list_vens()
        return web.json_response(
            [ven.dict() for ven in vens if id is None or id == ven.id]
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
    async def get(self, id: str, /) -> Union[r200[Ven], r404[Error]]:
        """
        Find a ven by ID

        Status Codes:
            200: Successful operation
            404: Ven not found
        """
        ven = self.request.app["model"].find_ven(id)
        return web.json_response(ven.dict())

    async def put(self, id: str, /, ven: Ven) -> r200[Ven]:
        """
        Update an existing object

        Status Codes:
            200: Successful operation
            404: Ven not found
        """
        self.request.app["model"].update_ven(id, ven)
        return web.json_response(ven.dict())

    async def delete(self, id: str, /) -> r204:
        """
        Deletes a ven
        """
        self.request.app["model"].remove_ven(id)
        return web.Response(status=204)
