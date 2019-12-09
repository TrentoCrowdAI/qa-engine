#!/bin/bash

if test -f "service_start_save_pid.txt"; then
  kill -9 $(cat service_start_save_pid.txt)
  rm service_start_save_pid.txt
else
  echo "Service is not running..."
fi