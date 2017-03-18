import requests
import re
import shutil
import logging

class GoProCamera:

    def __init__(self, ip, password, jpegGetTimeout, otherGetTimeout):
        self._password = password
        self._apiUrl = "http://"+ip
        self._webUrl = self._apiUrl + ":8080"
        self._jpegGetTimeout = jpegGetTimeout
        self._otherGetTimeout = otherGetTimeout

    def _apiCall(self, api, method, cmdParam):
        parameter = ""
        if cmdParam is not None:
            if (type(cmdParam) is int) or cmdParam.isdigit():
                parameter = "&p=%0" + str(cmdParam)
            else:
                parameter = "&p=" + cmdParam
        url = "/".join((self._apiUrl, api, method))
        url += "?t=" + self._password + parameter
        logging.debug("Accessing URL %s", url)
        try:
            r = requests.get(url, timeout=self._otherGetTimeout)
            logging.debug("HTTP Response %s", r.status_code)
            return {"status_code":r.status_code, "content":r.content}
        except requests.exceptions.Timeout as excp:
            logging.error("ApiCall - timeout exception %s", str(excp))
        except requests.exceptions.TooManyRedirects as excp:
            logging.critical("ApiCall - tooManyRedirects exception %s", str(excp))
        except requests.exceptions.RequestException as excp:
            logging.critical("ApiCall - request exception %s", str(excp))
        except excp:
            logging.critical("ApiCall - Other exception %s", str(excp))            
        return {"status_code": 400, "content": []}

    def _cameraApi(self, method, intParam=None):
        return self._apiCall('camera', method, intParam)

    def _bacpacApi(self, method, intParam=None):
        return self._apiCall('bacpac', method, intParam)

    def status(self):
        r = self._bacpacApi("se")
        logging.info("Status - HTTP result %s, Content %s", str(r["status_code"]), str(r["content"]))
        rslt = {"ready": False if len(r["content"])<15 else (r["content"][15] == 1)}
        rslt["bytes"] = [x for x in r["content"]]
        return rslt

    def powerOn(self):
        return self._bacpacApi('PW', 1)
    
    def powerOff(self):
        return self._bacpacApi('PW', 0)

    def startBeeping(self):
        return self._cameraApi('LL', 1)

    def stopBeeping(self):
        return self._cameraApi('LL', 0)

    def startCapture(self):
        return self._cameraApi('SH', 1)

    def stopCapture(self):
        return self._cameraApi('SH', 0)

    def deleteLast(self):
        return self._cameraApi('DL')

    def deleteAll(self):
        return self._cameraApi('DA')

    def listJpegs(self, path=None):
        url = self._webUrl + ("" if path==None else "/" + path)
        rslt = []
        try:
            r = requests.get(url, timeout=self._otherGetTimeout)
            # print(r.text)
            rslt = re.findall("\>(.+.JPG)\<", r.text)
            # print("search", rslt)
        except requests.exceptions.Timeout as excp:
            logging.error("List Jpegs - timeout exception %s", str(excp))
        except requests.exceptions.TooManyRedirects as excp:
            logging.critical("List Jpegs - tooManyRedirects exception %s", str(excp))
        except requests.exceptions.RequestException as excp:
            logging.critical("List Jpegs - request exception %s", str(excp))
        except excp:
            logging.critical("List Jpegs - Other exception %s", str(excp))            
        return rslt

    def listFolders(self, path=None):
        url = self._webUrl + ("" if path == None else "/" + path)
        rslt = []
        try:
            r = requests.get(url, timeout=self._otherGetTimeout)
            # print(r.text)
            rslt = re.findall("href\=\"(.+)\/\"\>", r.text)
            # print("search", rslt)
        except requests.exceptions.Timeout as excp:
            logging.error("List Folders - timeout exception %s", str(excp))
        except requests.exceptions.TooManyRedirects as excp:
            logging.critical("List Folders - tooManyRedirects exception %s", str(excp))
        except requests.exceptions.RequestException as excp:
            logging.critical("List Folders - request exception %s", str(excp))
        except excp:
            logging.critical("List Folders - Other exception %s", str(excp))            
        return rslt

    def getPhoto(self, srcPath, destPath, deleteLastAfterCopy=False):
        # Copy the file
        url = self._webUrl + ("" if srcPath == None else srcPath)
        logging.info("Get jpeg %s", str(url))
        try:
            success = False
            r = requests.get(url, stream=True, timeout=self._jpegGetTimeout)
            # Handle the success condition
            if r.status_code == 200:
                r.raw.decode_content = True
                try:
                    with open(destPath, 'wb') as f:
                        while True:
                            buf = None
                            try:
                                buf = r.raw.read(16*1024)
                            except excp:
                                logging.error("RawRead - Error %s", str(excp))
                            if not buf:
                                break
                            f.write(buf)
                        success = True
                except (OSError, IOError) as excp:
                    logging.error("CopyFile - File system error %s", str(excp))
                except excp:
                    logging.error("CopyFile - Other exception %s", str(excp))
            if success:
                logging.info("Copied Ok (%s) %s to %s ", str(r.status_code)), srcPath, destPath)
                # Delete the last file if it exists
                if deleteLastAfterCopy:
                    logging.info("Deleting the last file")
                    self.deleteLast()
            else:
                logging.info("Copy Failed %s to %s", srcPath, destPath)
        except requests.exceptions.Timeout as excp:
            logging.error("Copy - timeout exception %s", str(excp))
        except requests.exceptions.TooManyRedirects as excp:
            logging.critical("Copy - tooManyRedirects exception %s", str(excp))
        except requests.exceptions.RequestException as excp:
            logging.critical("Copy - request exception %s", str(excp))
        except excp:
            logging.critical("Copy - Other exception %s", str(excp))

if __name__ == "__main__":
    cam = GoProCamera('10.5.5.9', "password")
    print(cam.status())
    print(cam.listJpegs("/DCIM/100GOPRO"))
