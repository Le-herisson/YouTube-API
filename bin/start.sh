cd ..
export PATH="./bin/:$PATH"
uvicorn --host 0.0.0.0 --port 2684 --log-level info --use-colors main:app --ssl-certfile ./certs/cert.pem --ssl-keyfile ./certs/key.pem