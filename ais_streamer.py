import json
import asyncio
import websockets

stop_flag = False
JSON_PATH = "ais_position.json"

# Clear the JSON files
def clear_json():
    with open(JSON_PATH, "w") as f:
        json.dump([], f)

# Append websocket data to the JSON
def append_to_json(data):
    with open(JSON_PATH, "r") as f:
        existing = json.load(f)
    existing.append(data)
    with open(JSON_PATH, "w") as f:
        json.dump(existing, f)

def run_websockets_loop():
    asyncio.run(stream_ais_position())

# ASYNC WEBSOCKET FOR POSITION DATA
async def stream_ais_position():
    global stop_flag
    uri = "wss://stream.aisstream.io/v0/stream"
    subscribe_message = {
        "APIKey": "124f9a783325c6d6ec7402febf532fca3d6eb34d",
        "BoundingBoxes": [[[25.835302, -80.207729], [25.602700, -79.879297]], [[33.772292, -118.356139], [33.673490, -118.095731]]],
        "FilterMessageTypes": ["PositionReport"]
    }

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(subscribe_message))
            while not stop_flag:
                try:
                    message_json = await asyncio.wait_for(websocket.recv(), timeout=5)
                    message = json.loads(message_json)
                    if message.get("MessageType") == "PositionReport":
                        data = message["Message"]["PositionReport"]
                        metadata = message['MetaData']
                        data = {
                            "timestamp": metadata['time_utc'],
                            "MMSI": metadata['MMSI'],
                            "ShipName": metadata['ShipName'].strip(),
                            "lat": data["Latitude"],
                            "lon": data["Longitude"]
                        }
                        append_to_json(data)
                except asyncio.TimeoutError:
                    continue
    except Exception as e:
        print("WebSocket Error:", e)
