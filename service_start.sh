#!/bin/bash

if ! test -f "service_start_save_pid.txt"; then
  source venv3.7/bin/activate
  pip install -r requirements_python2.txt
  pip3 install -r requirements_python3.txt
  nohup gunicorn --bind 0.0.0.0:80 app:app > my.log 2>&1 &
  echo $! > service_start_save_pid.txt
else
  echo "Service is running... stop it before starting again"
fi