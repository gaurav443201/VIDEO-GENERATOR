#!/bin/bash

# Start the background audio/video compilation daemon
echo "Starting VidSnapAI video queue daemon..."
python generate_process.py &

# Start the Gunicorn web server to serve traffic
echo "Starting Flask web server on port $PORT..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 main:app
