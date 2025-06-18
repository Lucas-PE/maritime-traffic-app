import json
import asyncio
import websockets
import os

stop_flag = False
uri = "wss://stream.aisstream.io/v0/stream"
POSITION_JSON_PATH = "data/ais_position.json"
STATIC_JSON_PATH = "data/ais_static.json"
API_KEY = '124f9a783325c6d6ec7402febf532fca3d6eb34d'
bbox = [[[47.707669,-5.666748], [48.851501,-3.947388]]]

# Clear the JSON files
def clear_json():
    for json_path in [POSITION_JSON_PATH, STATIC_JSON_PATH]:
        with open(json_path, "w") as f:
            json.dump([], f)

# Append websocket data to the JSON
def append_to_json(data, filename):
    with open(filename, "r") as f:
        existing = json.load(f)
    existing.append(data)
    with open(filename, "w") as f:
        json.dump(existing, f, indent=2)


async def run_websockets_loop():
    await asyncio.gather(
        stream_ais_position(bbox),
        stream_ais_static(bbox),
    )


# WEBSOCKET FOR STATIC DATA --> Trigger for each new MMSI position   
async def stream_ais_static(bbox):
    global stop_flag
    subscribe_message = {
        "APIKey": API_KEY,
        "BoundingBoxes": bbox,
        "FilterMessageTypes": ["ShipStaticData"]
        }
    try:
        # Connect to AIS
        async with websockets.connect(uri) as websocket:
            # Send position message
            await websocket.send(json.dumps(subscribe_message))
            while not stop_flag:
                # Retreive Data
                try:
                    message_json = await asyncio.wait_for(websocket.recv(), timeout = 10)
                    message = json.loads(message_json)
                    if message.get("MessageType") == "ShipStaticData":
                        data = message["Message"]["ShipStaticData"]
                        metadata = message['MetaData']
                        data = {
                            "timestamp": metadata['time_utc'],
                            "MMSI": metadata["MMSI"],
                            "Destination": data["Destination"],
                            "Dimension": data["Dimension"],
                            "Eta": data["Eta"],
                            "Type": data["Type"],
                        }
                        append_to_json(data, STATIC_JSON_PATH)
                        
                except asyncio.TimeoutError:
                    continue
    except Exception as e:
        print("WebSocket Error:", e)


# ASYNC WEBSOCKET FOR POSITION DATA
async def stream_ais_position(bbox):
    global stop_flag
    subscribe_message = {
        "APIKey": API_KEY,
        "BoundingBoxes": bbox,
        "FilterMessageTypes": ["PositionReport"]
        }
    try:
        # Connect to AIS
        async with websockets.connect(uri) as websocket:
            # Send position message
            await websocket.send(json.dumps(subscribe_message))
            while not stop_flag:
                # Retreive Data
                try:
                    message_json = await asyncio.wait_for(websocket.recv(), timeout=5)
                    message = json.loads(message_json)
                    if message.get("MessageType") == "PositionReport":
                        data = message["Message"]["PositionReport"]
                        metadata = message['MetaData']
                        data = {
                            "timestamp": metadata['time_utc'],
                            "MMSI": metadata["MMSI"],
                            "ShipName": metadata['ShipName'].strip(),
                            "lat": data["Latitude"],
                            "lon": data["Longitude"],
                            "COG": data["Cog"],
                            "NavigationalStatus": data["NavigationalStatus"],
                            "RateOfTurn": data["RateOfTurn"],
                            "SOG": data["Sog"],
                            "Spare": data["Spare"],
                            "UserID": data["UserID"]
                        }
                        append_to_json(data, POSITION_JSON_PATH)
                        
                except asyncio.TimeoutError:
                    continue
    except Exception as e:
        print("WebSocket Error:", e)
