#!/usr/bin/env bash

# This script runs BOTH the FastAPI backend and the Streamlit frontend.
# It is designed to be used as the "Start Command" on platforms like Render.

# Exit early on errors
set -eu

# 1. Start the FastAPI backend in the background
echo "Starting FastAPI backend..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Wait a second for the backend to start
sleep 2

# 2. Start the Streamlit frontend in the foreground
# Streamlit will bind to the PORT environment variable provided by Render (or 10000 by default)
echo "Starting Streamlit frontend..."
streamlit run app.py --server.port ${PORT:-10000} --server.address 0.0.0.0
