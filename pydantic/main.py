from aiohttp.web import Application, json_response, middleware
from aiohttp import web
from aiohttp_pydantic import oas

from model import Model
from view import VenCollectionView, VenItemView


@middleware
async def ven_not_found_to_404(request, handler):
    try:
        return await handler(request)
    except Model.NotFound as key:
        return json_response({"error": f"Ven {key} does not exist"}, status=404)


app = Application(middlewares=[ven_not_found_to_404])
oas.setup(app, version_spec="1.0.1", title_spec="My App")

app["model"] = Model()
app.router.add_view("/vens", VenCollectionView)
app.router.add_view("/vens/{id}", VenItemView)


web.run_app(app)