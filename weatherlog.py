#!/usr/bin/python
from serial import serial
import time

class WeatherLogger(object):
    
    
    def __init__(self, path='/home/volker/weather/weather.log'):
        self.logger = Serial('/dev/ttyUSB0', baudrate=19200, bytesize=8, stopbits=1, timeout=0 )
        self.path = path
    
    def readData(self, maxtime=180):
        t = maxtime
        while t > 0:
            t = t-1
            b = self.logger.inWaiting()
            if b > 0:
                data = self.logger.read(b)
                self.writeData(data)
                return 1
            time.sleep(1)
        return 0
        
        
            
    def writeData(self, data):
        f = open(self.path,'w')
        f.write(data)
        f.write("\n")
        f.close()
    

def main():
    l = WeatherLogger()
    max = 100
    print ('Start Logging')
    while (max > 0):
        max = max-1
        ret = l.readData()
        if ret == 0:
            print ('No data received')
        else:
            print ('Data received')
    print ('End Logging')

main()