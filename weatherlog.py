#!/usr/bin/python
import serial
import time

class WeatherLogger(object):
    
    
    def __init__(self, path='/home/volker/weather/weather.log'):
        self.logger = serial.Serial('/dev/ttyUSB0', baudrate=19200, bytesize=8, stopbits=1, timeout=0 )
        self.path = path
    
        
    def readData(self):
        b = self.logger.inWaiting()
        if b > 0:
            return self.logger.read(b)
        return ''
        
    def readDataToFile(self, maxtime=180):
        t = maxtime
        while t > 0:
            t = t-1
            b = self.logger.inWaiting()
            if b > 0:
                data = self.logger.read(b)
                self.writeDataToFile(data)
                return 1
            time.sleep(1)
        return 0
        
            
    def writeDataToFile(self, data):
        with open(self.path,'a') as f:
            f.write(currentTime() + "\n")
            f.write(data)
    
    def logInfo(self):
        self.logger.write("?")
        time.sleep(1)
        ret = self.readData()
        if (len(ret) == 0):
            print 'ERROR: Logger info could not be read!'
            return -1
        else:
            print ret
            return 1

  
def currentTime():
    ts=time.time()
    crt = time.strftime("%Y-%m-%d %H:%M:%S.",time.localtime(ts))
    return str(crt)
        
def main():
    l = WeatherLogger()
    i = l.logInfo()
    if i < 0:
        return 0
        
    max = 100
    print (currentTime())
    print ('Start Logging')
    while (max > 0):
        max = max-1
        ret = l.readDataToFile()
        print (currentTime())
        if ret == 0:
            print ('No data received')
        else:
            print ('Data received')
    print ('End Logging')

main()