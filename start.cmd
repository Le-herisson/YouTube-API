@ECHO off
TITLE API on 127.0.0.1:2684
ECHO Open http://127.0.0.1:2684/
venv\Scripts\activate.bat & uvicorn --host 127.0.0.1 --port 2684 --reload --log-level info --use-colors main:app & venv\Scripts\deactivate
EXIT/B
