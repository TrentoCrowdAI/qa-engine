#!/bin/bash

if ! test -f "service_start_save_pid.txt"; then
  nohup gunicorn --bind 0.0.0.0:5000 app:app > my.log 2>&1 &
  echo $! > service_start_save_pid.txt
else
  echo "Service is running... stop it before starting again"
fi