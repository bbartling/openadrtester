import asyncio
from typing import Any, AsyncIterator, Awaitable, Callable, Dict
from datetime import datetime, timezone, timedelta
import pytz
from openleadr import OpenADRServer, enable_default_logging
from functools import partial
import time
from aiohttp import web
import jinja2
import aiohttp_jinja2
import logging
import os

enable_default_logging(logging.DEBUG)
#enable_default_logging()


# convert form data to UTC for openleadr
def convert_to_utc(time, tzname, date=None, is_dst=None):
    tz = pytz.timezone(tzname)
    if date is None: # use date from current local time in tz
        date = datetime.now(tz).date()

    dt = tz.localize(datetime.combine(date, time), is_dst=is_dst)
    return dt.astimezone(pytz.utc), dt.utcoffset().total_seconds()



# Future db
event_id_storage = []
vens_info_storage = []


# form data lookup for creating an event with the html page
def find_ven_in_ven_storage(data):
    for vens in vens_info_storage.values():
        print(v['ven_id'])
        if vens.get('ven_id') == data:
            return True
        else:
            return False


def find_ven_in_event_storage(data):
    for vens in event_id_storage.values():
        print(v['ven_id'])
        if vens.get('ven_id') == data:
            return True
        else:
            return False


def handle_json_error(
    func: Callable[[web.Request], Awaitable[web.Response]]
) -> Callable[[web.Request], Awaitable[web.Response]]:
    async def handler(request: web.Request) -> web.Response:
        try:
            return await func(request)
        except asyncio.CancelledError:
            raise
        except Exception as ex:
            return web.json_response(
                {"status": "failed", "info": str(ex)}, status=400
            )

    return handler



'''
OPEN LEADR CONFIG
'''

async def on_create_party_registration(registration_info):
    """
    Inspect the registration info and return a ven_id and registration_id.
    """
    print("TRYING TO LOOK UP VEN FOR REGISTRATION: ",registration_info['ven_name'])

    ven_name = registration_info['ven_name']
    for v in VENS.values():
        #print(values['ven_name'])
        if v.get('ven_name') == ven_name:
            print(f"REGISTRATION SUCCESS WITH NAME:  {v.get('ven_name')} FROM PAYLOAD, MATCH FOUND {ven_name}")
            return v['ven_id'],v['registration_id']
        else:
            print("REGISTRATION FAIL BAD VEN NAME: ",registration_info['ven_name'])
            return False


 
async def on_register_report(ven_id, resource_id, measurement, unit, scale,
                             min_sampling_interval, max_sampling_interval):
    """
    Inspect a report offering from the VEN and return a callback and sampling interval for receiving the reports.
    """
    callback = partial(on_update_report, ven_id=ven_id, resource_id=resource_id, measurement=measurement)
    sampling_interval = min_sampling_interval
    return callback, sampling_interval

async def on_update_report(data, ven_id, resource_id, measurement):
    """
    Callback that receives report data from the VEN and handles it.
    """
    for time, value in data:
        print(f"Ven {ven_id} reported {measurement} = {value} at time {time} for resource {resource_id}")

async def event_response_callback(ven_id, event_id, opt_type):
    """
    Callback that receives the response from a VEN to an Event.
    """
    print(f"VEN {ven_id} responded to Event {event_id} with: {opt_type}")



'''
async def handle_cancel_event(request):
    """
    Handle a cancel event request.
    """
    try:
        ven_id = request.match_info['ven_id']
        print(request)

        # look up function to see if this VEN exists
        if find_ven(ven_id):

            print("HANDLE CANCEL EVENT find_ven(ven_id) ", find_ven(ven_id))


            server = request.app["server"]
            server.cancel_event(ven_id=str(ven_id),
                event_id="our-event-id",
            )

            tz_Chicago = pytz.timezone('America/Chicago') 
            datetime_Chicago = datetime.now(tz_Chicago)
            datetime_Chicago_formated = datetime_Chicago.strftime("%H:%M:%S")
            info = f"Event canceled now at Chicago time:, {datetime_Chicago_formated}"
            response_obj = { 'status' : 'success', 'info' : info }
            return web.json_response(response_obj)

        else:
            response_obj = { 'status' : 'failed', 'info' : 'bad ven name' }
            return web.json_response(response_obj, status=404)

    except Exception as e:
        ## Bad path where name is not set
        response_obj = { 'status' : 'failed', 'info': str(e) }
        ## return failed with a status code of 500 i.e. 'Server Error'
        return web.json_response(response_obj, status=500)

'''


'''
Non-open openLeadr endpoints
'''



@handle_json_error
async def all_event_info(request: web.Request) -> web.Response:
    print("all_event_info hit",time.ctime())
    return web.json_response(event_id_storage)




@handle_json_error
async def handle_create_event(request: web.Request) -> web.Response:
    args = await request.json()
    #data = {'value': args['key']}
    print(args)
    return web.json_response(args)




@handle_json_error
async def handle_cancel_event(request: web.Request) -> web.Response:
    args = await request.json()
    data = {'value': args['key']}
    print(data)
    return web.json_response(data)




@handle_json_error
async def handle_add_vens(request: web.Request) -> web.Response:

    args = await request.json()
    data = {
        "ven_name": args["ven_name"],
        "ven_id": args["ven_id"],
        "registration_id": args["registration_id"],
        "site_address": args["site_address"],
        "utility_provider_id": args["utility_provider_id"]
        }

    vens_info_storage.append(data)

    return web.json_response({"status": "success", "info": data})




@handle_json_error
async def handle_delete_vens(request: web.Request) -> web.Response:

    args = await request.json()
    data = {"ven_name": args["ven_name"]}

    return web.json_response(data)



@handle_json_error
async def handle_all_vens(request: web.Request) -> web.Response:
    print("handle_all_vens hit",time.ctime())
    return web.json_response({"status": "success", "info": vens_info_storage})



# Create the server object
server = OpenADRServer(vtn_id='cloudvtn',
                        http_host='0.0.0.0',
                        #ven_lookup=ven_lookup_function
                        )



# Add the handler for client (VEN) registrations
server.add_handler('on_create_party_registration', on_create_party_registration)
# Add the handler for report registrations from the VEN
server.add_handler('on_register_report', on_register_report)



server.app.add_routes([
    web.get('/api/all-events', all_event_info),
    web.post('/api/add-event', handle_create_event),
    web.post('/api/delete-event', handle_cancel_event),
    web.post('/api/add-vens', handle_add_vens),
    web.post('/api/delete-vens', handle_delete_vens),
    web.get('/api/all-vens', handle_all_vens)
])


# Run the server on the asyncio event loop
loop = asyncio.get_event_loop()
loop.create_task(server.run())
loop.run_forever()



'''
    web.get('/trigger-event/{ven_id}', handle_trigger_event),
    web.get('/cancel-event/{ven_id}', handle_cancel_event),
'''
