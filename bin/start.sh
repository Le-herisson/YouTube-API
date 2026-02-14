cd ..
export PATH="./bin/:$PATH"
export roFs=false
ECHO Open http://127.0.0.1:2684/
uvicorn --host 0.0.0.0 --port 2684 --log-level info --use-colors main:app --ssl-certfile ./certs/cert.pem --ssl-keyfile ./certs/key.pem