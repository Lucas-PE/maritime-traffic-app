import os
from os import path
import dash
from dash import Dash, page_container
from flask import Flask
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
from functions.ais_streamer import stop_websockets
import atexit
from flask import request


atexit.register(stop_websockets)


def create_app() -> Dash:
    """Construct the core application."""
    
    app = Flask(__name__, static_folder='assets')
    
    @app.route("/shutdown", methods=["POST"])
    def shutdown_websocket():
        stop_websockets()
        return "WebSocket stopped", 200
    
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
