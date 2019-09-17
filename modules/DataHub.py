import requests
from requests.auth import HTTPBasicAuth
# import datetime
import time
import json
import base64
import cv2
import pprint
import numpy as np

from enum import Enum


class request(Enum):
  GETROBOTSTATUSLIST = 0
  GETROBOTSTATUS = 1
  PUTROBOTSTATUS = 2
  POSTROBOTSTATUS = 3
  GETLOCATIONLIST = 4
  GETLOCATION = 5
  PUTLOCATION = 6
  POSTLOCATION = 7
  GETPATIENTLIST = 8
  GETPATIENT = 9
  GETIMAGELIST = 10
  GETIMAGE = 11
  PUTIMAGE = 12
  POSTIMAGE = 13
# from io import StringIO

currentTimeID = str(int(time.time()*1000000))
currentTime = str(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(int(int(time.time())))))

###Variables to get  from other parts of the interface. #####
StatusMessage = "test message to be changed"
currentStatus = "Loading"
droneX = 0
droneY = 0
droneZ = 0

getImageFile = 'some1.jpeg'
###end data from other parts of interface #####

#encoding the image for apiObj.Put/PostImage()
with open(getImageFile, mode='rb') as file: 
  img = file.read()
encodedImage = json.dumps(base64.b64encode(img).decode("utf-8"))


## Constant Variables 
teamid ='bathdrones'
teamkey = 'd22ec71d-af83-4cd6-847c-ea5031870d9b'
baseurl = "https://api.mksmart.org/sciroc-competition/"
robotName = "Gary"
ID = teamid + "-" + robotName + "-" + currentTimeID

#Json Data
Status_Info = {
  "@id": ID,
  "@type": "RobotStatus",
  "message": "loading",
  "episode": "EPISODE12",
  "team": "bathdrones",
  "timestamp": currentTime,
  "x": droneX, 
  "y": droneY,
  "z": droneZ
}

Robot_Location = {
  "@id": ID,
  "@type": "RobotLocation",
  "episode": "EPISODE12", 
  "team": "string",
  "timestamp": currentTime,
  "x": droneX, 
  "y": droneY,
  "z": droneZ
}

Patient= {
  "@id": ID,
  "@type": "Patient",
  "x": droneX, 
  "y": droneY,
  "z": droneZ
}

ImageReport = {
  "@id": ID,
  "@type": "ImageReport",
  "team": "bathdrones",
  "timestamp": currentTime,
  "x": 0,
  "y": 0,
  "z": 0,
  "base64": encodedImage,
  "format": "image/jpeg"
  }


class API:
  def __init__(self):
    pass

  def PrintData(self,response):
    print("Server Status: "+str(response.status_code) +"\n")
    #print(response.text)

  def POST(self,url, payload):
    response = requests.request("POST",url, data=payload, auth=HTTPBasicAuth(teamkey, ''))
    self.PrintData(response)

  def PUT(self,url, payload):
    response = requests.request("PUT",url, data=payload, auth=HTTPBasicAuth(teamkey, ''))
    self.PrintData(response)

  def GET(self,url):
    response = requests.request("GET",url, auth=HTTPBasicAuth(teamkey, ''))
    self.PrintData(response)
    getData = json.loads(response.text)[0]
    pprint.pprint(getData)
    return getData
    
  ##StatusBlock
  def GetRobotStatusList(self):
    url = baseurl +  teamid + '/sciroc-robot-status/'
    self.GET(url)

  def GetRobotStatus(self, getID):
    url = baseurl +  teamid + '/sciroc-robot-status/' + getID 
    self.GET(url)
  
  def PutRobotStatus(self):
    payload = json.dumps(Status_Info)
    url = baseurl +  teamid + "/sciroc-robot-status/" + ID
    self.PUT(url, payload)

  def PostRobotStatus(self):
    payload = json.dumps(Status_Info)
    url = baseurl +  teamid + "/sciroc-robot-status/" + ID
    self.POST(url,payload)
  
  ##Location Block
  def GetLocationList(self):
    url = baseurl +  teamid + "/sciroc-robot-location/"
    self.GET(url)

  def GetLocation(self, getID):
    url = baseurl +  teamid +"/sciroc-robot-location/" + getID
    self.GET(url)

  def PutLocation(self):
    url = baseurl +  teamid +"/sciroc-robot-location/" + ID
    payload = json.dumps(Robot_Location)
    self.PUT(url,payload)
 
  def PostLocation(self):
    url = baseurl +  teamid + "/sciroc-robot-location/" + ID
    payload = json.dumps(Robot_Location)
    self.POST(url,payload)

  ##Patient Block
  def GetPatientList(self):
    url = baseurl + "/master/sciroc-episode12-patient/"
    getData = self.GET(url)

    print("ID is = "+str(getData["@id"]))


  def GetPatient(self, getID):
    url = baseurl + "/master/sciroc-episode12-patient/" + getID 
    self.GET(url)
    getData = self.GET(url)
    patientX = getData["x"]
    patientY = getData["y"]
    patientZ = getData["z"]
    return patientX, patientY, patientZ

  ##Image Block
  def GetImageList(self):
    url = baseurl +  teamid + "/sciroc-episode12-image/"
    #payload = json.dumps(ImageReport)
    self.GET(url)

  def GetImage(self, getID):
    url = baseurl +  teamid + "/sciroc-episode12-image/" + getID 
    getData = self.GET(url)
    getImageData = getData["base64"]
    #print(getImageData)
    decodedImage = base64.b64decode(getImageData)
    img = cv2.imdecode(np.frombuffer(decodedImage, dtype=np.uint8), 1)
    cv2.imshow("img",img)
    cv2.waitKey(1000)

  def PutImage(self):
    url = baseurl +  teamid + "/sciroc-episode12-image/" + ID 
    payload = json.dumps(ImageReport)
    self.PUT(url, payload)

  def PostImage(self):
    url = baseurl +  teamid + "/sciroc-episode12-image/" + ID 
    payload = json.dumps(ImageReport)
    self.POST(url, payload)


apiObj = API()
request = request.GETROBOTSTATUSLIST


if request == request.GETROBOTSTATUSLIST:
  apiObj.GetRobotStatusList()

elif request == request.GETROBOTSTATUS:
  getID = 'someInputID'
  apiObj.GetRobotStatus(getID)

elif request == request.PUTROBOTSTATUS:
  apiObj.PutRobotStatus()

elif request == request.POSTROBOTSTATUS:
  apiObj.PostRobotStatus()

elif request == request.GETLOCATIONLIST:
  apiObj.GetRobotStatusList()

elif request == request.GETLOCATION:
  getID = 'someInputID'
  apiObj.GetLocation(getID)

elif request == request.PUTLOCATION:
  apiObj.PutLocation()
  
elif request == request.POSTLOCATION:
  apiObj.PostLocation()
  
elif request == request.GETPATIENTLIST:
  apiObj.GetPatientList()
  
elif request == request.GETPATIENT:
  getID = 'someInputID'
  apiObj.GetPatient(getID)
  
elif request == request.GETIMAGELIST:
  apiObj.GetImageList()
  
elif request == request.GETIMAGE:
  getID = 'someInputID'
  apiObj.GetImage(getID)
  
elif request == request.PUTIMAGE:
  apiObj.PutImage()
  
elif request == request.POSTIMAGE:
  apiObj.PostImage()
  

#apiObj.GetPatient(getID)


# print(currentTimeID)



