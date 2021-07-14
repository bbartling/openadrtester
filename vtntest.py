import asyncio
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
VENS = {
    "dan_test": {"ven_name": "dan_test", "ven_id": "ven_id_dan_test", "registration_id": "reg_id_dan_test"},
    "slipstream_ven1": {"ven_name": "slipstream_ven1", "ven_id": "ven_id_slipstream_ven1", "registration_id": "reg_id_slipstream_ven1"},
    "volttron_test": {"ven_name": "volttron_test", "ven_id": "ven_id_volttron_test", "registration_id": "reg_id_volttron_test"}     
}


# form data lookup for creating an event with the html page
def find_ven(form_data):
    for v in VENS.values():
        print(v['ven_id'])
        if v.get('ven_id') == form_data:
            return True
        else:
            return False

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


async def handle_trigger_event(request):
    """
    Handle a trigger event request.
    """
    try:
        ven_id = request.match_info['ven_id']

        # look up function to see if this VEN exists
        if find_ven(ven_id):

            print("HANDLE TRIGGER EVENT find_ven(ven_id) ", find_ven(ven_id))

            server = request.app["server"]
            server.add_event(ven_id=str(ven_id),
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
            data = f"Event added now at Chicago time:, {datetime_Chicago_formated}"
            response_obj = { 'status' : 'success', 'info' : data }
            return web.json_response(response_obj)

        else:
            response_obj = { 'status' : 'failed', 'reason' : 'bad ven name' }
            return web.json_response(response_obj, status=404)

    except Exception as e:
        ## Bad path where name is not set
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        ## return failed with a status code of 500 i.e. 'Server Error'
        return web.json_response(response_obj, status=500)


async def handle_cancel_event(request):
    """
    Handle a cancel event request.
    """
    try:
        ven_id = request.match_info['ven_id']

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
            data = f"Event canceled now at Chicago time:, {datetime_Chicago_formated}"
            response_obj = { 'status' : 'success', 'info' : data }
            return web.json_response(response_obj)

        else:
            response_obj = { 'status' : 'failed', 'reason' : 'bad ven name' }
            return web.json_response(response_obj, status=404)

    except Exception as e:
        ## Bad path where name is not set
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        ## return failed with a status code of 500 i.e. 'Server Error'
        return web.json_response(response_obj, status=500)


'''
APP SPLASH PAGE TO ENTER DATE TIME FOR DR EVENT
'''

@aiohttp_jinja2.template("index.html")
async def index_handler(request):
    return {}


async def form_grabber(request: web.Request) -> web.Response:

    try:
        #db = request.config_dict["DB"]
        post = await request.post()
        print("FORM GRABBER ", post)

        stamp = time.time()
        Date = datetime.fromtimestamp(stamp)
        sec_microsec_adder = ':0:0'
        sec_adder = ':0'

        # convert multidict to dict
        data = {}
        for k in set(post.keys()):
            k_values = post.getall(k)
            if len(k_values) > 1:
                data[k] = k_values
            else:
                data[k] = k_values[0]

        ven_id = data['VEN ID']
        print("FORM GRABBER VEN_ID", ven_id)

        minutes = int(data['Minutes'])

        # look up function to see if this VEN exists
        if find_ven(ven_id):

            print("FORM GRABBER find_ven(ven_id) ",find_ven(ven_id))

            event_start = data['Event-Start'] + sec_microsec_adder
            print("Event-Start is ",event_start)

            f = "%Y-%m-%dT%H:%M:%S:%f"
            event_start_formatted = datetime.strptime(event_start, f)
            print("event_start_formatted is ",event_start_formatted)
            event_start_formatted_local_tz = pytz.utc.localize(event_start_formatted)
            print("event_start_formatted_local_tz is ",event_start_formatted_local_tz)

            time_only = event_start_formatted_local_tz.time()
            print("time_only is ",time_only)
            date_only = event_start_formatted_local_tz.date()
            print("date_only is ",date_only)
            event_start_utc, offset = convert_to_utc(time_only, 'America/Chicago', date_only)
            print("Event-Start-UTC is ",event_start_utc)

            print(f"open ADR event will be {event_start_formatted_local_tz} local tz for {minutes} minutes")
            print(f"open ADR event will be {event_start_utc} UTC tz for {minutes} minutes")

            """
            Handle a trigger event request with openleadr.
            """
            server = request.app["server"]
            server.add_event(ven_id=ven_id,
                signal_name='LOAD_CONTROL',
                signal_type='x-loadControlCapacity',
                intervals=[{'dtstart': event_start_utc,
                            'duration': timedelta(minutes=minutes),
                            'signal_payload': 1.0}],
                callback=event_response_callback,
                event_id="our-event-id",
            )

            response_obj = { 'status' : 'success', 'info' : data }
            return web.json_response(response_obj)

        else:
            response_obj = { 'status' : 'failed', 'reason' : 'bad ven name' }
            return web.json_response(response_obj, status=404)


    except Exception as e:
        ## Bad path where name is not set
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        ## return failed with a status code of 500 i.e. 'Server Error'
        return web.json_response(response_obj, status=500)


'''
APP CONFIG
'''


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
    web.get('/', index_handler),
    web.post('/transform', form_grabber),
    web.get('/trigger-event/{ven_id}', handle_trigger_event),
    web.get('/cancel-event/{ven_id}', handle_cancel_event),
])


aiohttp_jinja2.setup(
    server.app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates"))
)


# Run the server on the asyncio event loop
loop = asyncio.get_event_loop()
loop.create_task(server.run())
loop.run_forever()
