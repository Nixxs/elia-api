#!/bin/bash
gunicorn --workers 3 --timeout 200 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 "elia_api.main:app"