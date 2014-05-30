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
        
    def readDataToFile(self, maxtime=180, sleeptime=30):
        if sleeptime < 1:
            return 'ERROR: sleeptime < 1 not allowed';
        t = maxtime
        while t > 0:
            t = t-sleeptime
            b = self.logger.inWaiting()
            if b > 0:
                data = self.logger.read(b)
                self.writeDataToFile(data)
                return data
            time.sleep(sleeptime)
        return ''
        
            
    def writeDataToFile(self, data):
        with open(self.path,'a') as f:
            f.write(currentTime() + "\n")
            f.write(data)
    
    def logInfo(self):
        self.logger.write("?")
        time.sleep(1)
        ret = self.readData()
        if (len(ret) == 0):
            log('ERROR: Logger info could not be read!')
            return -1
        else:
            log(ret)
            return 1

def log(string):
    print currentTime() + " - " + string
    
def currentTime():
    ts=time.time()
    crt = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ts))
    return str(crt)
        
def main():
    l = WeatherLogger()
    i = l.logInfo()
    if i < 0:
        return 0
        
    #max = 100
    log('Start Logging')
    while (1==1):
        #max = max-1
        data = l.readDataToFile()
        if len(data) == 0:
            log ('No data received')
        else:
            log ('Data received: ' + data)
    log ('End Logging')

main()