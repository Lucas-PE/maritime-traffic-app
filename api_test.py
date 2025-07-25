import pandas as pd
import asyncio
import websockets
import json
from datetime import datetime, timezone

async def connect_ais_stream():

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {'APIKey': '124f9a783325c6d6ec7402febf532fca3d6eb34d', 
                             'BoundingBoxes': [[[40.990243933837384, -33.75000000000001], [49.61729630536983, 4.218750000000001]]], 
                            #  'FiltersShipMMSI': ["215170000"], 
                             'FilterMessageTypes': ['PositionReport']}

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                # ais_message = message['Message']['PositionReport']
                # metadata_message = message['MetaData']
                # print(f"[{metadata_message['time_utc']}] MMSI: {metadata_message['MMSI_String']} ShipName: {metadata_message['ShipName']} Latitude: {ais_message['Latitude']} Latitude: {ais_message['Longitude']}")
                print(message)

if __name__ == "__main__":
    asyncio.run(connect_ais_stream())