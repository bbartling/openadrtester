
import asyncio
import json
from openleadr import OpenADRClient, enable_default_logging
import aiohttp

from datetime import timezone,date,datetime,timedelta
import datetime


import logging

enable_default_logging(logging.INFO)







async def collect_report_value():
    """
    read json data collected & saved from BACnet BAC0 app
    """

    return 12.3


async def handle_event(event):
    """
    Do something based on the event.
    """


    print(f'[EVENT INFO!!!!] - {event}')
    event_time = event['event_signals'][0]['intervals'][0]['dtstart']   
    print(f'[EVENT TIME!!!!] - {event_time}') 


    loop = asyncio.get_event_loop()
    signal = event['event_signals'][0]
    intervals = signal['intervals']
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    for interval in intervals:
        start = interval['dtstart']
        delay = (start - now_utc).total_seconds()
        value = interval['signal_payload']
        duration = interval['duration']
        delay_info = f"Setting DR Signal of {value} after {round(delay/60/60)} hours {round(delay/60)} minutes timer expires for {duration} H/M/S"
        print(delay_info)

        loop.create_task(change_status(status=int(value),
                                       delay=delay))
 
    payload_objects = {}
    payload_objects[f'dtstart'] = interval['dtstart'].strftime('UTC Time Zone, %a %m-%d-%Y at %r')
    payload_objects[f'duration'] = str(interval['duration'])
    payload_objects[f'signal_payload'] = interval['signal_payload']

    print(payload_objects)

    return 'optIn'

# Create the client object
client = OpenADRClient(ven_name='ben_house',
                       vtn_url='http://localhost:8080/OpenADR2/Simple/2.0b')


# Add the report capability to the client
client.add_report(callback=collect_report_value,
                  resource_id='building main egauge',
                  measurement='power',
                  sampling_rate=timedelta(seconds=120))

# Add event handling capability to the client
client.add_handler('on_event', handle_event)

# Run the client in the Python AsyncIO Event Loop
loop = asyncio.get_event_loop()
loop.create_task(client.run())
loop.run_forever()