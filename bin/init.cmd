@ECHO off
CD ..
python -m venv venv
venv/scripts/python -m pip install -r requirements.txt
start.cmd
ECHO Done !