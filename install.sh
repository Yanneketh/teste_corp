#!/bin/sh 
sleep 2 
python -m venv --clear /opt/venv 
/opt/venv/bin/pip install --no-cache-dir -r requirements.txt 
