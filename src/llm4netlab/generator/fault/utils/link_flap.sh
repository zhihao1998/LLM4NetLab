#!/bin/bash

IFACE=${1:-eth0}       
DOWN_TIME=${2:-1}
UP_TIME=${3:-1}

while true; do
    ip link set $IFACE down
    sleep $DOWN_TIME
    ip link set $IFACE up
    sleep $UP_TIME
done