#!/bin/bash

# Start the Gunicorn web server (contains the integrated worker thread)
echo "Starting Flask web server on port $PORT..."
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 main:app
