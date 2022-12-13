#!/usr/bin/env python
import os
import sys
import threading

class BashThread(threading.Thread):
    def __init__(self, name='bash-thread'):
        super().__init__(name=name)
        self.start()

    def run(self):
        os.system("bash /opt/pzserver/start-server.sh")

def callback(inp):
    print("Entered: ")

BashThread().run()
