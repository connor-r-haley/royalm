#!/bin/bash
cd "/Users/connorhaley/Desktop/royalm/backend"
source "/Users/connorhaley/Desktop/royalm/venv/bin/activate"
echo "📡 Starting backend server..."
python -m uvicorn main:app --reload --port 8001
