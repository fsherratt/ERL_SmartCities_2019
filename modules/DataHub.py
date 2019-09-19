import requests
from requests.auth import HTTPBasicAuth 
import time
import json
import base64
import cv2
import numpy as np
import scipy.misc


class API:
    teamid ='bathdrones'
    teamkey = 'd22ec71d-af83-4cd6-847c-ea5031870d9b'
    baseurl = "https://api.mksmart.org/sciroc-competition/"
    robotName = "Gary"
    episode = "EPISODE12"

    def __init__(self):
        self.position = [0,0,0]
        self.status = 'Loading'

    def ID(self):
        return self.teamid + "-" + self.robotName + "-" + self.currentTimeID()

    def currentTimeID(self):
        return str(int(time.time()*1000000))

    def currentTime(self):
        return str(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(int(int(time.time())))))

    def setPosition(self, newPos):
        self.position = newPos

    def setStatus(self, newStatus):
        self.status = newStatus

    def sendImage(self, img):
        imbyte = cv2.imencode(".png", img)[1].tostring()
        encodedImage = base64.b64encode(imbyte).decode('utf-8')
        self.PostImage(encodedImage)
    
    def Status_Info(self):
        Status_Info = {
            "@id": self.ID(),
            "@type": "RobotStatus",
            "message": self.status,
            "episode": self.episode,
            "team": self.teamid,
            "timestamp": self.currentTime(),
            "x": self.position[0], 
            "y": self.position[1],
            "z": self.position[2]
        }
        return Status_Info

    def Robot_Location(self):
        Robot_Location = {
            "@id": self.ID(),
            "@type": "RobotLocation",
            "episode": self.episode, 
            "team": self.teamid,
            "timestamp": self.currentTime(),
            "x": self.position[0], 
            "y": self.position[1],
            "z": self.position[2]
        }
        return Robot_Location

    def ImageReport(self, img):
        ImageReport = {
            "@id": self.ID(),
            "@type": "ImageReport",
            "team": self.teamid,
            "timestamp": self.currentTime(),
            "x": self.position[0], 
            "y": self.position[1],
            "z": self.position[2],
            "base64": "data:image/png;base64," + img,
            "format": "image/jpeg"
        }
        return ImageReport

    def PrintData(self,response):
        print("Server Status: "+str(response.status_code) +"\n")

    def POST(self,url, payload):
        response = requests.request("POST",url, data=payload, auth=HTTPBasicAuth(self.teamkey, ''))
        self.PrintData(response)

    def PUT(self,url, payload):
        response = requests.request("PUT",url, data=payload, auth=HTTPBasicAuth(self.teamkey, ''))
        self.PrintData(response)

    def GET(self,url):
        response = requests.request("GET",url, auth=HTTPBasicAuth(self.teamkey, ''))
        #self.PrintData(response)
        getData = json.loads(response.text)[0:5]
        return getData

    # StatusBlock
    def GetRobotStatusList(self):
        url = self.baseurl + self.teamid + '/sciroc-robot-status/'
        result = self.GET(url)
        return result

    def GetRobotStatus(self, getID):
        url = self.baseurl + self.teamid + '/sciroc-robot-status/' + getID 
        result = self.GET(url)
        return result

    def PutRobotStatus(self):
        payload = json.dumps(self.Status_Info())
        url = self.baseurl + self.teamid + "/sciroc-robot-status/" + self.ID()
        self.PUT(url, payload)

    def PostRobotStatus(self):
        payload = json.dumps(self.Status_Info())
        url = self.baseurl + self.teamid + "/sciroc-robot-status/" + self.ID()
        self.POST(url,payload)

    # Location Block
    def GetLocationList(self):
        url = self.baseurl + self.teamid + "/sciroc-robot-location/"
        result = self.GET(url)
        return result

    def GetLocation(self, getID):
        url = self.baseurl +  self.teamid +"/sciroc-robot-location/" + self.ID()
        result = self.GET(url)
        return result

    def PutLocation(self):
        url = self.baseurl + self.teamid +"/sciroc-robot-location/" + self.ID()
        payload = json.dumps(self.Robot_Location())
        self.PUT(url,payload)

    def PostLocation(self):
        url = self.baseurl + self.teamid + "/sciroc-robot-location/" + self.ID()
        payload = json.dumps(self.Robot_Location())
        self.POST(url,payload)

    # Patient Block
    def GetPatientList(self):
        url = self.baseurl + "/master/sciroc-episode12-patient/"
        result = self.GET(url)
        return result

    def GetPatient(self, getID):
        url = self.baseurl + "/master/sciroc-episode12-patient/" + getID 
        self.GET(url)
        result = self.GET(url)[0]
        patientLocation = [result["x"], result["y"], result["z"]]
        return patientLocation, result

    # Image Block
    def GetImageList(self):
        url = self.baseurl + self.teamid + "/sciroc-episode12-image/"
        result = self.GET(url)
        return result

    def GetImage(self, getID):
        url = self.baseurl + self.teamid + "/sciroc-episode12-image/" + getID 
        result = (self.GET(url)[0])["base64"]
        # decodedImage = base64.b64decode(str(result["base64"])[22:0]) ####to put decoding inside 
        # img = cv2.imdecode(np.frombuffer(decodedImage, dtype=np.uint8), 1) ####to put decoding inside
        return result

    def PutImage(self, img):
        url = self.baseurl + self.teamid + "/sciroc-episode12-image/" + self.ID() 
        payload = json.dumps(self.ImageReport(img))
        self.PUT(url, payload)

    def PostImage(self, img):
        url = self.baseurl + self.teamid + "/sciroc-episode12-image/" + self.ID() 
        payload = json.dumps(self.ImageReport(img))
        self.POST(url, payload)


if __name__ == "__main__":
    apiObj = API()

    from modules.realsense.d435 import rs_d435

    d435Obj = rs_d435()
    
    with d435Obj:
        i = 0
        while i<1:
            # id =  'bathdrones-Gary-1568881509221367'#imgList[0]['@id']
            # print(id)

            ##To post image
            # _, img = d435Obj.getFrame()
            # apiObj.sendImage(img)

            ##To get patient Location
            Pateint_Location = apiObj.GetPatient('P001')[0]
            print("Patient Location: "+str(Pateint_Location))
            
            ##To get robot Location
            # apiObj.GetLocationList()
            # apiObj.GetLocation(id)

            #print(robotstatus)
            #imgList = apiObj.GetImageList()

            ##Code to gdecode Img
            # getImg = (apiObj.GetImage(id))[22:]            
            # decodedImage = base64.b64decode(getImg)
            # img = cv2.imdecode(np.frombuffer(decodedImage, dtype=np.uint8), 1)
            # cv2.imshow("img", img)
            # cv2.waitKey(1000)
            ##Code to get Img end
            i = 1
        pass
