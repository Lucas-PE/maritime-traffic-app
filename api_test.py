import pandas as pd
import asyncio
import websockets
import json
from datetime import datetime, timezone

async def connect_ais_stream():

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": "124f9a783325c6d6ec7402febf532fca3d6eb34d",  # Required !
                             "BoundingBoxes": [[[25.835302, -80.207729], [25.602700, -79.879297]], [[33.772292, -118.356139], [33.673490, -118.095731]] ], # Required!
                            #  "FiltersShipMMSI": ["368207620", "367719770", "211476060"], # Optional!
                             "FilterMessageTypes": ["PositionReport"]} # Optional!

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                ais_message = message['Message']['PositionReport']
                metadata_message = message['MetaData']
                print(f"[{metadata_message['time_utc']}] MMSI: {metadata_message['MMSI_String']} ShipName: {metadata_message['ShipName']} Latitude: {ais_message['Latitude']} Latitude: {ais_message['Longitude']}")

if __name__ == "__main__":
    asyncio.run(connect_ais_stream())