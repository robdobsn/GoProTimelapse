from GoProCamera import GoProCamera
import time, datetime
import configparser
import logging

# Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

# Get config
config = configparser.ConfigParser()
config.read("config.ini")
cameraPassword = config["Camera"]["Password"]

jpegFolder = "/DCIM/100GOPRO"

cam = GoProCamera('10.5.5.9', cameraPassword, 60, 60)
print("Camera status", cam.status())
jpegList = cam.listJpegs(jpegFolder)
print("Current num files", len(jpegList))

doit = input("Delete all files? (yes/no)")
if doit.upper() == "YES":
    cam.deleteAll()
    time.sleep(3.0)
    jpegList = cam.listJpegs(jpegFolder)
    print("Current num files", len(jpegList))
else:
    print("Not deleted")
    
