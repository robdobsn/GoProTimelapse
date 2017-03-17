import requests
import re
import shutil

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
        print(url)
        try:
            r = requests.get(url, timeout=self._otherGetTimeout)
            print("HTTP Response", r.status_code)
            return {"status_code":r.status_code, "content":r.content}
        except requests.exceptions.Timeout as excp:
            print("ApiCall - timeout exception", excp)
        except requests.exceptions.TooManyRedirects as excp:
            print("ApiCall - tooManyRedirects exception", excp)
        except requests.exceptions.RequestException as excp:
            print("ApiCall - request exception", excp)
        return {"status_code": 400, "content": []}

    def _cameraApi(self, method, intParam=None):
        return self._apiCall('camera', method, intParam)

    def _bacpacApi(self, method, intParam=None):
        return self._apiCall('bacpac', method, intParam)

    def status(self):
        r = self._bacpacApi("se")
        print("Status - HTTP result", r["status_code"], "Content", r["content"])
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
            print("List Jpegs - timeout exception", excp)
        except requests.exceptions.TooManyRedirects as excp:
            print("List Jpegs - tooManyRedirects exception", excp)
        except requests.exceptions.RequestException as excp:
            print("List Jpegs - request exception", excp)
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
            print("List Folders - timeout exception", excp)
        except requests.exceptions.TooManyRedirects as excp:
            print("List Folders - tooManyRedirects exception", excp)
        except requests.exceptions.RequestException as excp:
            print("List Folders - request exception", excp)
        return rslt

    def getPhoto(self, srcPath, destPath, deleteLastAfterCopy=False):
        # Copy the file
        url = self._webUrl + ("" if srcPath == None else srcPath)
        print("Get jpeg", url)
        try:
            success = False
            r = requests.get(url, stream=True, timeout=self._jpegGetTimeout)
            # Handle the success condition
            if r.status_code == 200:
                r.raw.decode_content = True
                imgData = r.raw
                try:
                    with f = open(destPath, 'wb') as f:
                        f.write(imgData)
                        success = True
                except (OSError, IOError) as excp:
                    print("File system error", excp)
            if success:
                print("Copy", srcPath, "to", destPath, "result", r.status_code)
                # Delete the last file if it exists
                if deleteLastAfterCopy:
                    print("Deleting the last file")
                    self.deleteLast()
            else:
                print("Copy", srcPath, "to", destPath, "failed")
        except requests.exceptions.Timeout as excp:
            print("Copy - timeout exception", excp)
        except requests.exceptions.TooManyRedirects as excp:
            print("Copy - tooManyRedirects exception", excp)
        except requests.exceptions.RequestException as excp:
            print("Copy - request exception", excp)

if __name__ == "__main__":
    cam = GoProCamera('10.5.5.9', "password")
    print(cam.status())
    print(cam.listJpegs("/DCIM/100GOPRO"))
