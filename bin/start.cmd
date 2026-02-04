@ECHO off
CD ..
SET "PATH=%PATH%;./bin/"
TITLE API on 127.0.0.1:2684
ECHO Open https://127.0.0.1:2684/
venv\Scripts\activate.bat & uvicorn --host 0.0.0.0 --port 2684 --log-level info --use-colors main:app --ssl-certfile ./certs/cert.pem --ssl-keyfile ./certs/key.pem & venv\Scripts\deactivate
EXIT/B
