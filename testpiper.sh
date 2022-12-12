#!/usr/bin/env bash
while [ true ] ; do
  read -p "Say yes or no" yn
  case $yn in
    [Yy]* ) echo "Yes!";;
    [Nn]* ) echo "No!";;
    * ) echo "What?";;
  esac
done
