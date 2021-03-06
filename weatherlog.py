#!/usr/bin/python
import serial
import time
import sqlite3 as db
from ISStreamer.Streamer import Streamer

# --------- User Settings ---------
BUCKET_NAME = "bucket_name"
BUCKET_KEY = "bucket_key"
ACCESS_KEY = "access_key"
MINUTES_BETWEEN_WRITES = 30
# ---------------------------------
class WeatherLogger(object):


    def __init__(self, path='~/weather/weather.log'):
        self.logger = serial.Serial('/dev/ttyUSB0', baudrate=19200, bytesize=8, stopbits=1, timeout=0 )
        self.path = path
        self.dbPath = 'weather.sqlite'
        self.streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
        self.streamer.log("Weatherlog Msg", "Start streaming...")


    def connectDB(self):
        self.dbConn = db.connect(self.dbPath)
        self.dbCursor = self.dbConn.cursor()

    def closeDB(self):
        self.dbConn.close()

    def readData(self):
        b = self.logger.inWaiting()
        if b > 0:
            return self.logger.read(b)
        return ''

    def readDataToDB(self, maxtime=180, sleeptime=30):
        if sleeptime < 1:
            return 'ERROR: sleeptime < 1 not allowed'
        t = maxtime
        while t > 0:
            t = t-sleeptime
            b = self.logger.inWaiting()
            if b > 0:
                data = self.logger.read(b)
                self.writeDataToDB(data)
                return data
            time.sleep(sleeptime)
        return ''

    def writeDataToDB(self, data):
        self.connectDB()
        # $1;1;;;;;;;;;;;;;;;;;;12,4;82;0,0;40;0;0
        dataArr = data.split(';')
        date = currentTime()
        temp = dataArr[19]
        hum = dataArr[20]
        wind = dataArr[21]
        rain = dataArr[22]
        rain_curr = dataArr[23]
        rowdata = (None, date, temp, hum, wind, rain, rain_curr)
        # save in db
        self.dbCursor.execute('insert into weatherdata values(?, ?, ?, ?, ?, ?, ?)', rowdata)
        self.dbConn.commit()
        self.closeDB()

    def writeDataToIS(self, data):
        dataArr = data.split(';')
        date = currentTime()
        temp = dataArr[19]
        hum = dataArr[20]
        wind = dataArr[21]
        rain = dataArr[22]
        rain_curr = dataArr[23]
        self.streamer.log("Temperatur(C)", temp)
        self.streamer.log("Luftfeuchtigkeit(%)", hum)
        self.streamer.log("Wind(km/h)", wind)
        self.streamer.log("Regen", rain_curr)
        self.streamer.log("Regenmenge", rain)
        self.streamer.flush()

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
    lastSentToIS=0
    while (1==1):
        #max = max-1
        data = l.readDataToDB()
        if len(data) == 0:
            log ('No data received')
        else:
            log ('Data received: ' + data)
            if (time.time() > (lastSentToIS + MINUTES_BETWEEN_WRITES*60)):
                log ('Send to IS...')
                lastSentToIS = time.time()
                l.writeDataToIS(data)

    log ('End Logging')

main()
