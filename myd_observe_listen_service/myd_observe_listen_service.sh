#!/bin/bash

echo "starting MyDaemon listner"
python3 /home/pi/src/MyDaemon/myd_observe_listen_service/myd_listen_pi.py --broker "192.168.1.72"
