#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oscilloscope with incoming HTTP data via Flask (graphing by Bokeh)
Persistent data across sessions using a global deque with a maximum length.
Each data point is stored as a tuple (seq, x, y). When new data comes in,
if the deque is full, older data is dropped. Each Bokeh session uses the
sequence numbers to determine what new data to stream.
"""

import argparse
import threading
from collections import deque
from functools import partial

from bokeh.server.server import Server
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.layouts import column

from flask import Flask, request, jsonify

# -------------------------------
# Global Data Store for Persistence
# -------------------------------
# global_data will be a deque of tuples (seq, x, y)
global_data = None  
global_data_lock = threading.Lock()

# Global sequence counter for incoming data.
global_counter = 0

# ------------------------
# Flask Application Setup
# ------------------------

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    """
    Receives incoming data via an HTTP POST.
    Expected JSON payload: {"x": <number>, "y": <number>}
    """
    global global_counter
    try:
        data = request.get_json(force=True)
        x_value = float(data['x'])
        y_value = float(data['y'])
    except (KeyError, TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid data format. Expected JSON with keys 'x' and 'y'."}), 400

    # Append the new data point to the global_data deque with a sequence number.
    with global_data_lock:
        seq = global_counter
        global_counter += 1
        global_data.append((seq, x_value, y_value))
    return jsonify({"status": "success"}), 200

def run_flask_server(port):
    """
    Run the Flask app on the specified port.
    """
    app.run(host='0.0.0.0', port=port)

# --------------------------
# Bokeh Application Setup
# --------------------------

def bk_app(doc, scope_points):
    """
    Bokeh document that creates an "oscilloscope" which updates with data
    from the global deque. Each new session is initialized with the current
    persistent data.
    """
    # Initialize the session's data source with the current contents of global_data.
    with global_data_lock:
        current_list = list(global_data)
    initial_data = {
        'x': [pt[1] for pt in current_list],
        'y': [pt[2] for pt in current_list]
    }
    source = ColumnDataSource(data=initial_data)

    # Create the plot.
    p = figure(x_axis_label="X", y_axis_label="Y",
               toolbar_location=None, sizing_mode='stretch_both')
    p.line(x='x', y='y', source=source, line_width=2, line_color="red")

    # Add a hover tool.
    hover = HoverTool(tooltips=[("x", "@x"), ("y", "@y")])
    p.add_tools(hover)

    # Add the plot to the document.
    doc.add_root(column(p, sizing_mode='stretch_both'))
    doc.theme = 'dark_minimal'

    # Use a mutable container to track the sequence number of the last streamed point.
    # If there is no data yet, initialize to -1.
    last_seq = [current_list[-1][0] if current_list else -1]

    def update():
        """
        Periodic callback that checks the global_data deque for any new data (based on
        sequence numbers) and streams that data into the session's ColumnDataSource.
        """
        with global_data_lock:
            current_list = list(global_data)
        if not current_list:
            return
        # If the first element in the deque has a sequence number greater than
        # last_seq[0], then the deque has "rolled over" (older items have been dropped).
        if last_seq[0] < current_list[0][0]:
            # Stream the entire deque.
            new_items = current_list
        else:
            # Stream only items with sequence number greater than last_seq[0]
            new_items = [pt for pt in current_list if pt[0] > last_seq[0]]
        if new_items:
            last_seq[0] = new_items[-1][0]
            new_data = {
                'x': [pt[1] for pt in new_items],
                'y': [pt[2] for pt in new_items]
            }
            source.stream(new_data, rollover=scope_points)

    # Call the update function every 100 milliseconds.
    doc.add_periodic_callback(update, 100)

# -------------------------
# Main entry point
# -------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Oscilloscope that displays data received via HTTP POST (using Flask) "
                    "with persistent graphing by Bokeh and a capped global store.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-p", "--port", help="Bokeh server port (oscilloscope display)", default=5001, type=int)
    parser.add_argument("-f", "--flask_port", help="Flask server port (for incoming data)", default=5002, type=int)
    parser.add_argument("-s", "--scope_points",
                        help="Total points shown in the oscilloscope and stored in memory",
                        default=1023, type=int)
    args = parser.parse_args()

    # Initialize global_data as a deque with a maximum length.
    global_data = deque(maxlen=args.scope_points)

    # Start the Flask server in a separate daemon thread.
    flask_thread = threading.Thread(target=run_flask_server, args=(args.flask_port,), daemon=True)
    flask_thread.start()
    print(f"Flask server running on port {args.flask_port}...")

    # Set up and start the Bokeh server.
    bokeh_apps = {'/': partial(bk_app, scope_points=args.scope_points)}
    server = Server(bokeh_apps, port=args.port, address="0.0.0.0")
    server.start()
    print(f"Bokeh server running on port {args.port}...")

    try:
        server.io_loop.start()
    except KeyboardInterrupt:
        print("Keyboard interruption detected. Shutting down.")
