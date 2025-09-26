import json
import asyncio
import websockets
import os
import threading
import time

stop_event = threading.Event()
uri = os.getenv("URI")
API_KEY = os.getenv("API_KEY")
POSITION_JSON_PATH = "data/raw/ais_position.json"
STATIC_JSON_PATH = "data/raw/ais_static.json"

# Stop websocket
def stop_websockets():
    stop_event.set()
    time.sleep(1)
    clear_json(POSITION_JSON_PATH, STATIC_JSON_PATH)
    print("🛑 WebSocket loop stop signal sent. JSON cleared")

# Clear the JSON files
def clear_json(static_json_path, position_json_path):
    for json_path in [static_json_path, position_json_path]:
        with open(json_path, "w") as f:
            json.dump([], f)


# Append websocket data to the JSON
def append_to_json(data, filename):
    with open(filename, "r") as f:
        existing = json.load(f)
    existing.append(data)
    with open(filename, "w") as f:
        json.dump(existing, f, indent=2)


# WEBSOCKET FOR STATIC DATA --> Trigger for each new MMSI position   
async def stream_ais_static(bbox, static_json_path):
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
            while not stop_event.is_set():
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
                        append_to_json(data, static_json_path)
                        
                except asyncio.TimeoutError:
                    continue
    except Exception as e:
        print("WebSocket Error:", e)


# ASYNC WEBSOCKET FOR POSITION DATA
async def stream_ais_position(bbox, position_json_path):
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
            while not stop_event.is_set():
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
                            "UserID": data["UserID"],
                            "Heading": data["TrueHeading"]
                        }
                        append_to_json(data, position_json_path)
                        
                except asyncio.TimeoutError:
                    continue
    except Exception as e:
        print("WebSocket Error:", e)
