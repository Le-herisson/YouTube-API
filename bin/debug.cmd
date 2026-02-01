@ECHO off
CD ..
TITLE YouTube-API on 127.0.0.1:2684
ECHO Open http://127.0.0.1:2684/
venv\Scripts\activate.bat & uvicorn --host 0.0.0.0 --port 2684 --log-level info --use-colors --reload main:app & venv\Scripts\deactivate
EXIT/B
