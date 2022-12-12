#!/usr/bin/env bash
echo "awaiting input"
while [ true ] ; do
  read -t 3 -n 1
  if [ $? = 0 ] ; then
    exit ;
  else
    echo "awaiting input"
  fi
done
