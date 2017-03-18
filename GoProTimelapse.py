from GoProCamera import GoProCamera
import time, datetime
import configparser
import logging
from subprocess import call

# Logging
#logging.basicConfig(filename="GoProTimelapse.log", level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

# Get config
config = configparser.ConfigParser()
config.read("config.ini")
cameraPassword = config["Camera"]["Password"]

# Note that these must not have a trailing /
jpegFolder = "/DCIM/100GOPRO"
destFolder = "/mnt/synologyScratch/timelapse"

# Intervals and timeouts
exposureTimeSecs = 0.05
timelapseInterval = 30.0
jpegGetTimeout = 120.0
otherGetTimeout = 60.0

logging.info("GoProTimelapse, Rob Dobson 2017")
#time.sleep(60)

cam = GoProCamera('10.5.5.9', cameraPassword, jpegGetTimeout, otherGetTimeout)
logging.info("Camera status %s", str(cam.status()))
logging.info("Current num files %s", str(len(cam.listJpegs(jpegFolder))))

curTime = datetime.datetime.now()

while(True):

    # Show time and difference from last
    #print("Time", curTime.strftime("%Y-%m-%d %H:%M:%S"), "Seconds since last = ", (datetime.datetime.now() - curTime).seconds)
    logging.info("Seconds since last = %s", str((datetime.datetime.now() - curTime).seconds))
    curTime = datetime.datetime.now()

    # Capture photo
    cam.startCapture()
    time.sleep(exposureTimeSecs)
    cam.stopCapture()

    # Wait for file to appear in the list - this does not happen immediately
    time.sleep(5.0)

    # Extract files from camera
    fileList = cam.listJpegs(jpegFolder)
    logging.info("Current num files %s", str(len(fileList)))
    for fileName in reversed(fileList):
        srcPath = jpegFolder + "/" + fileName
        destPath = destFolder + "/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".JPG"
        cam.getPhoto(srcPath, destPath, True)
        newFileList = cam.listJpegs(jpegFolder)
        logging.info("Current num files %s", str(len(newFileList)))

    # Delay between photos
    while(datetime.datetime.now() < curTime + datetime.timedelta(seconds=timelapseInterval)):
        time.sleep(0.1)
