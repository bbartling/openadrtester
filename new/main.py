from aiohttp.web import Application, json_response, middleware
from aiohttp import web
from aiohttp_pydantic import oas

from model import Model
from view import VenCollectionView, VenItemView
from view import EventCollectionView, EventItemView



@middleware
async def ven_not_found_to_404(request, handler):
    try:
        return await handler(request)
    except Model.NotFound as key:
        return json_response({"error": f"Ven {key} does not exist"}, status=404)


@middleware
async def event_not_found_to_404(request, handler):
    try:
        return await handler(request)
    except Model.NotFound as key:
        return json_response({"error": f"Event {key} does not exist"}, status=404)


#app = Application(middlewares=[ven_not_found_to_404],middlewares=[event_not_found_to_404])
app = Application(middlewares=[ven_not_found_to_404,event_not_found_to_404])
oas.setup(app, version_spec="1.0.1", title_spec="Open ADR VTN Server")

app["model"] = Model()
app.router.add_view("/vens", VenCollectionView)
app.router.add_view("/vens/{ven_name}", VenItemView)
app.router.add_view("/events", EventCollectionView)
app.router.add_view("/events/{event_id}", EventItemView)

web.run_app(app)