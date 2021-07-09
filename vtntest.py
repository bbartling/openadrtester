import asyncio
from datetime import datetime, timezone, timedelta
import pytz
from openleadr import OpenADRServer, enable_default_logging
from functools import partial

from aiohttp import web

import logging
enable_default_logging(logging.DEBUG)
#enable_default_logging()


async def on_create_party_registration(registration_info):
    """
    Inspect the registration info and return a ven_id and registration_id.
    """
    if registration_info['ven_name'] == 'slipstream_ven1':
        ven_id = 'ven_id_slipstream_ven1'
        registration_id = 'reg_id_slipstream_ven1'
        return ven_id, registration_id

    if registration_info['ven_name'] == 'dan_test':
        ven_id = 'ven_id_dan_test'
        registration_id = 'reg_id_dan_test'
        return ven_id, registration_id

    else:
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


async def handle_trigger_event(request):
    """
    Handle a trigger event request.
    """
    server = request.app["server"]
    server.add_event(ven_id='ven_id_dan_test',
        signal_name='LOAD_CONTROL',
        signal_type='x-loadControlCapacity',
        intervals=[{'dtstart': datetime.now(timezone.utc),
                    'duration': timedelta(minutes=10),
                    'signal_payload': 1.0}],
        callback=event_response_callback,
        event_id="our-event-id",
    )

    tz_Chicago = pytz.timezone('America/Chicago') 
    datetime_Chicago = datetime.now(tz_Chicago)
    datetime_Chicago_formated = datetime_Chicago.strftime("%H:%M:%S")
    text = f"Event added now at Chicago time:, {datetime_Chicago_formated}"
    return web.Response(text=text)


async def handle_cancel_event(request):
    """
    Handle a cancel event request.
    """
    server = request.app["server"]
    server.cancel_event(ven_id='ven_id_dan_test',
        event_id="our-event-id",
    )

    tz_Chicago = pytz.timezone('America/Chicago') 
    datetime_Chicago = datetime.now(tz_Chicago)
    datetime_Chicago_formated = datetime_Chicago.strftime("%H:%M:%S")
    text = f"Event canceled now at Chicago time:, {datetime_Chicago_formated}"
    return web.Response(text=text)


# Create the server object
server = OpenADRServer(vtn_id='cloudvtn',http_host='0.0.0.0')

# Add the handler for client (VEN) registrations
server.add_handler('on_create_party_registration', on_create_party_registration)

# Add the handler for report registrations from the VEN
server.add_handler('on_register_report', on_register_report)

server.app.add_routes([
    web.get('/trigger-event', handle_trigger_event),
    web.get('/cancel-event', handle_cancel_event),
])

# Add a prepared event for a VEN that will be picked up when it polls for new messages.
# server.add_event(ven_id='ven_id_slipstream_ven1',
#                  signal_name='LOAD_CONTROL',
#                  signal_type='x-loadControlCapacity',
#                  intervals=[{'dtstart': datetime.now(timezone.utc) + timedelta(minutes=5),
#                              'duration': timedelta(minutes=10),
#                              'signal_payload': 1.0}],
#                  callback=event_response_callback)

# Run the server on the asyncio event loop
loop = asyncio.get_event_loop()
loop.create_task(server.run())
loop.run_forever()
