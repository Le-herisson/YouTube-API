@ECHO off
python -m venv venv
venv/scripts/python -m pip install -r requirements.txt
venv/scripts/activate & start.cmd
