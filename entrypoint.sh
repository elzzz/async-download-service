#!/usr/bin/env bash

apt update
apt install -y zip

pip install -r requirements.txt
python server.py