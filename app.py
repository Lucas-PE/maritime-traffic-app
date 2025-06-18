import threading
import time
from ais_streamer import run_websockets_loop, clear_json

if __name__ == "__main__":
    try:
        clear_json()
        stop_flag = False
        print("WebSocket thread started. Collecting data...")

        # Start the WebSocket listener in background thread
        t = threading.Thread(target=run_websockets_loop, daemon=True)
        t.start()
        
        # Block the main thread (simulate app running)
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Interrupted. Shutting down.")

        # # Run Dash server (this blocks until closed)
        # app.run_server(debug=True)

    finally:
        # Cleanup when app stops
        print("Cleaning up...")
        stop_flag = True
        clear_json()