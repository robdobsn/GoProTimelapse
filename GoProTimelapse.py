from GoProCamera import GoProCamera
import time, datetime
import ConfigParser

# Get config
config = ConfigParser.ConfigParser()
config.read("config.ini")
cameraPassword = config["Camera"]["Password"]

# Note that these must not have a trailing /
jpegFolder = "/DCIM/100GOPRO"
destFolder = "/mnt/synologyScratch/timelapse"

# Intervals and timeouts
exposureTimeSecs = 0.1
timelapseInterval = 30.0
jpegGetTimeout = 30.0
otherGetTimeout = 5.0

print("GoProTimelapse, Rob Dobson 2017, Sleeping for 60 seconds ...")
time.sleep(60)

cam = GoProCamera('10.5.5.9', cameraPassword, jpegGetTimeout, otherGetTimeout)
print("Camera status", cam.status())
print("Current files", cam.listJpegs(jpegFolder))

curTime = datetime.datetime.now()

while(True):

    # Show time and difference from last
    print("Time", curTime.strftime("%Y-%m-%d %H:%M:%S"), "Seconds since last = ", (datetime.datetime.now() - curTime).seconds)
    curTime = datetime.datetime.now()

    # Capture photo
    cam.startCapture()
    time.sleep(exposureTimeSecs)
    cam.stopCapture()

    # Wait for file to appear in the list - this does not happen immediately
    time.sleep(5.0)

    # Extract files from camera
    fileList = cam.listJpegs(jpegFolder)
    print("Current files", fileList)
    for fileName in reversed(fileList):
        srcPath = jpegFolder + "/" + fileName
        destPath = destFolder + "/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".JPG"
        cam.getPhoto(srcPath, destPath, True)
        newFileList = cam.listJpegs(jpegFolder)
        print("Current files", newFileList)

    # Delay between photos
    while(datetime.datetime.now() < curTime + datetime.timedelta(seconds=timelapseInterval)):
        time.sleep(0.1)
