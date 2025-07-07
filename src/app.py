import threading
import time
from functions.ais_streamer import run_websockets_loop, clear_json
import asyncio
import os
from os import path
import dash
from dash import Dash, page_container
from flask import Flask
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

# def run_loop():
#     asyncio.run(run_websockets_loop())

# if __name__ == "__main__":
#     try:
#         clear_json()
#         stop_flag = False
#         print("WebSocket thread started. Collecting data...")

#         # Start the WebSocket listener in background thread
#         t = threading.Thread(target=run_loop, daemon=True)
#         t.start()
        
#         # Block the main thread (simulate app running)
#         while True:
#             time.sleep(1)
    
#     except KeyboardInterrupt:
#         print("Interrupted. Shutting down.")

#         # # Run Dash server (this blocks until closed)
#         # app.run_server(debug=True)

#     finally:
#         # Cleanup when app stops
#         print("Cleaning up...")
#         stop_flag = True
#         # clear_json()

def create_app() -> Dash:
    """Construct the core application."""
    
    app = Flask(__name__, static_folder='assets')
    with app.app_context():
        from components.layout import layout

        dash_app = Dash(__name__,
                        server=app,
                        url_base_pathname='/maritime_traffic/',
                        assets_folder='assets',
                        use_pages=True,
                        pages_folder='pages',
                        serve_locally=True,
                        external_stylesheets=[dbc.themes.BOOTSTRAP])

        # dash_app._favicon = "nagravision.svg"
        dash_app.title = 'MY APP'        
        dash_app.layout = layout(page_container)
        return dash_app


if __name__ == "__main__":
    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, "..", "..", ".env"))
    
    dash_app = create_app()
    
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    debug = False if os.environ.get("RENDER") else True
    
    pages = dash.page_registry.values()
    for page in pages:
        print(page["path"])
    dash_app.run(
        debug= debug,
        host = host,
        port= port
        )
        
