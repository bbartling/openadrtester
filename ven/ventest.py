import aiofiles
import asyncio
import json
from openleadr import OpenADRClient, enable_default_logging
import aiohttp

from datetime import timezone,date,datetime,timedelta
import datetime


import logging
#enable_default_logging(logging.DEBUG)
enable_default_logging(logging.INFO)
#enable_default_logging()




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

        sig_on = {"signal_payload": 1}
        async with aiofiles.open('event_signal_payload.json', 'w') as outfile:
            await outfile.write(json.dumps(sig_on))
            
        logging.debug(f"DR EVENT ON {sig_on}")
        print(f"DR EVENT ON {sig_on}")
        
        logging.debug("DR EVENT DURATION SLEEP START")
        print("DR EVENT DURATION SLEEP START")
        
        '''            
        await asyncio.sleep(duration)
        
        logging.debug("DR EVENT DURATION SLEEP EXPIRED")
        print("DR EVENT DURATION SLEEP EXPIRED")
        status = 0
        
        async with aiofiles.open('event_signal_payload.json', 'w') as outfile:
            await outfile.write(json.dumps(sig_off))
            
        '''
            
    elif status == 0 and STATUS == 1:
        logging.debug("DR EVENT OFF")
        print("DR EVENT OFF")

        sig_off = {"signal_payload": 0}
        async with aiofiles.open('event_signal_payload.json', 'w') as outfile:
            await outfile.write(json.dumps(sig_off))

    STATUS = status
    logging.debug(f"STATUS is {STATUS}")
    print(f"STATUS is {STATUS}")


async def collect_report_value():
    """
    read json data collected & saved from BACnet BAC0 app
    """
    async with aiofiles.open('power_meter_data.json', mode='r') as f:
        contents = await f.read()
    power = json.loads(contents)
    power = power['kW']
    print(f'JSON data for power is {power} kW')

    return power


async def handle_event(event):
    """
    Do something based on the event.
    """
    global STATUS


    logging.info(f'[EVENT INFO!!!!] - {event}')
    print(f'[EVENT INFO!!!!] - {event}')

    event_time = event['event_signals'][0]['intervals'][0]['dtstart']
    logging.info(f'[EVENT TIME!!!!] - {event_time}')    
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
        logging.info(delay_info)
        print(delay_info)
        '''
        loop.create_task(change_status(status=int(value),
                                       delay=delay),
                                       duration=duration)
        '''
        loop.create_task(change_status(status=int(value),
                                       delay=delay))
 
    payload_objects = {}

    '''
    psuedocode for when working beyond open ADR simple signal
    
    count = 1
    for interval in intervals:
        payload_objects[f'dtstart_{count}'] = interval['dtstart'].strftime('%a %Y-%m-%d %I %M %r')
        payload_objects[f'duration_{count}'] = str(interval['duration'])
        payload_objects[f'signal_payload_{count}'] = interval['signal_payload']
        count += 1
    '''


    payload_objects[f'dtstart'] = interval['dtstart'].strftime('UTC Time Zone, %a %m-%d-%Y at %r')
    payload_objects[f'duration'] = str(interval['duration'])
    payload_objects[f'signal_payload'] = interval['signal_payload']

    async with aiofiles.open('event_info.json', 'w') as outfile:
        await outfile.write(json.dumps(payload_objects))


    sig = {"signal_payload": STATUS}
    async with aiofiles.open('event_signal_payload.json', 'w') as outfile:
        await outfile.write(json.dumps(sig))

    return 'optIn'

# Create the client object
client = OpenADRClient(ven_name='slipstream_ven1',
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