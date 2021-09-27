
import asyncio
import json
from openleadr import OpenADRClient, enable_default_logging
import aiohttp

from datetime import timezone,date,datetime,timedelta
import datetime,time
import logging

enable_default_logging(logging.INFO)


headers = {'content-type': 'application/json'}
energy_meter_url = "http://192.168.0.100:5000/bacnet/read/single"
energy_meter_bacnet = {"address":"12345:2",
                "object_type":"analogInput",
                "object_instance":"2"}



STATUS = 0
def get_status():
    return STATUS


#async def change_status(status, delay, duration):
async def change_status(status, delay):
    """
    Change the switch position after 'delay' seconds.
    """
    global STATUS

    if delay > 0:
        await asyncio.sleep(delay)

    if status == 1 and STATUS == 0:

        print(f"[VEN INFO] change_status WRITE BACnet ON HERE ",time.ctime())
        print("[VEN INFO] change_status DR EVENT DURATION SLEEP START")

    elif status == 0 and STATUS == 1:

        print("[VEN INFO] change_status DR EVENT OFF")
        print(f"[VEN INFO] change_status WRITE BACnet OFF HERE ",time.ctime())

    STATUS = status
    print(f"[VEN INFO] change_status STATUS is {STATUS}")




async def collect_report_value():
    """
    Hit a Flask App REST endpoint every x seconds to get power data
    on a aiohttp client session
    """

    async with aiohttp.ClientSession(headers=headers) as session:

        async with session.get(energy_meter_url,
        json=energy_meter_bacnet) as req:

            print("[VEN INFO] Energy Meter Read Status ",req.status)
            payload = await req.json()
            power = payload["pv"]
            status = payload["status"]
            print("[VEN INFO] Energy Meter Read Status ",status)
            print("[VEN INFO] Energy Meter Read Value ",power)
            
            if status == "success":
                return power
            else:
                print("[VEN INFO] Energy Meter Read Error")
                return 0.0


async def handle_event(event):
    """
    Do something based on the event.
    """


    print(f'[VEN INFO] {event}')
    event_time = event['event_signals'][0]['intervals'][0]['dtstart']   
    print(f'[VEN INFO] {event_time}') 


    loop = asyncio.get_event_loop()
    signal = event['event_signals'][0]
    intervals = signal['intervals']
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    for interval in intervals:
        start = interval['dtstart']
        delay = (start - now_utc).total_seconds()
        value = interval['signal_payload']
        duration = interval['duration']
        delay_info = f"[VEN INFO] Setting DR Signal of {value} after {round(delay/60/60)} hours {round(delay/60)} minutes timer expires for {duration} H/M/S"
        print(delay_info)


        loop.create_task(change_status(status=int(value),
                               delay=delay))
 
    payload_objects = {}
    payload_objects[f'dtstart'] = interval['dtstart'].strftime('UTC Time Zone, %a %m-%d-%Y at %r')
    payload_objects[f'duration'] = str(interval['duration'])
    payload_objects[f'signal_payload'] = interval['signal_payload']

    print("[VEN INFO] Payload for Flask App ",payload_objects)

    return 'optIn'
    
    
    


# Create the client object
client = OpenADRClient(ven_name='ben_house',
                       vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')


# Add the report capability to the client
client.add_report(callback=collect_report_value,
                  resource_id='building main egauge',
                  measurement='power',
                  sampling_rate=timedelta(seconds=60))

# Add event handling capability to the client
client.add_handler('on_event', handle_event)

# Run the client in the Python AsyncIO Event Loop
loop = asyncio.get_event_loop()
loop.create_task(client.run())
loop.run_forever()