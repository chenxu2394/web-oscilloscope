#!/bin/sh
# Start the Python application in the background
python oscilloscope.py --port 5001 --flask_port 5002 --scope_points 1000 &

# Start Nginx in the foreground
nginx -g 'daemon off;'
