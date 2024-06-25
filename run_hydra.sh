#!/bin/bash
cd /data/hyDra
export FLASK_APP=RestServer
python3.7 -m flask run --host 0.0.0.0 --port 9000
