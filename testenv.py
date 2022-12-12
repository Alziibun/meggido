#!/usr/bin/env python
import os
import sys

while True:
    data = sys.stdin.readline()
    if len(data):
        print("[BASH]", data)
        os.system("echo two")