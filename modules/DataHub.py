import requests
from requests.auth import HTTPBasicAuth 
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
    #print(response.text)

  def POST(self,url, payload):
    response = requests.request("POST",url, data=payload, auth=HTTPBasicAuth(self.teamkey, ''))
    self.PrintData(response)

  def PUT(self,url, payload):
    response = requests.request("PUT",url, data=payload, auth=HTTPBasicAuth(self.teamkey, ''))
    self.PrintData(response)

  def GET(self,url):
    response = requests.request("GET",url, auth=HTTPBasicAuth(self.teamkey, ''))
    self.PrintData(response)
    getData = json.loads(response.text)[0]
    return getData
    
  ##StatusBlock
  def GetRobotStatusList(self):
    url = self.baseurl + self.teamid + '/sciroc-robot-status/'
    self.GET(url)

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
  
  ##Location Block
  def GetLocationList(self):
    url = self.baseurl + self.teamid + "/sciroc-robot-location/"
    result = self.GET(url)
    return result

  def GetLocation(self, getID):
    url = self.baseurl +  self.teamid +"/sciroc-robot-location/" + getID
    result = self.GET(url)
    return result

  def PutLocation(self):
    url = self.baseurl + self.teamid +"/sciroc-robot-location/" + self.ID()
    payload = json.dumps(self.Robot_Location())
    self.PUT(url,payload)
 
  def PostLocation(self):
    url = self.baseurl +  teamid + "/sciroc-robot-location/" + self.ID()
    payload = json.dumps(self.Robot_Location())
    self.POST(url,payload)

  ##Patient Block
  def GetPatientList(self):
    url = self.baseurl + "/master/sciroc-episode12-patient/"
    result = self.GET(url)
    return result
    # print("ID is = "+str(getData["@id"]))


  def GetPatient(self, getID):
    url = self.baseurl + "/master/sciroc-episode12-patient/" + getID 
    self.GET(url)
    result = self.GET(url)
    patientX = getData["x"]
    patientY = getData["y"]
    patientZ = getData["z"]
    return result, patientX, patientY, patientZ

  ##Image Block
  def GetImageList(self):
    url = self.baseurl + self.teamid + "/sciroc-episode12-image/"
    #payload = json.dumps(ImageReport)
    result = self.GET(url)
    return result

  def GetImage(self, getID):
    url = self.baseurl + self.teamid + "/sciroc-episode12-image/" + getID 
    result = self.GET(url)
    getImageData = result["base64"]
    #print(getImageData)
    decodedImage = base64.b64decode(getImageData)
    img = cv2.imdecode(np.frombuffer(decodedImage, dtype=np.uint8), 1)
    cv2.imshow("img",img)
    cv2.waitKey(1000)
    return result
    
  def PutImage(self, img):
    url = self.baseurl + self.teamid + "/sciroc-episode12-image/" + self.ID() 
    payload = json.dumps(self.ImageReport(img))
    print(payload)
    self.PUT(url, payload)

  def PostImage(self, img):
    url = self.baseurl + self.teamid + "/sciroc-episode12-image/" + self.ID() 
    payload = json.dumps(self.ImageReport(img))
    self.POST(url, payload)


if __name__ == "__main__":
  apiObj = API()
  
  getImageData = 'some1.jpeg'
  getID = '1568675071332568'

  imgFile = '/Users/omro/Dev/ERL_SmartCities_2019/modules/some1.jpeg'
  with open(imgFile, mode='rb') as file:
    img = file.read()

  encodedImage = base64.b64encode(img).decode('utf-8')
  apiObj.PutImage(encodedImage)


  '''
  if requiredData == request.GETROBOTSTATUSLIST:
    apiObj.GetRobotStatusList()

  elif requiredData == request.GETROBOTSTATUS:
    apiObj.GetRobotStatus(getID)

  elif requiredData == request.PUTROBOTSTATUS:
    apiObj.PutRobotStatus()

  elif requiredData == request.POSTROBOTSTATUS:
    apiObj.PostRobotStatus()

  elif requiredData == request.GETLOCATIONLIST:
    apiObj.GetLocationList()

  elif requiredData == request.GETLOCATION:
    apiObj.GetLocation(getID)

  elif requiredData == request.PUTLOCATION:
    apiObj.PutLocation()
    
  elif requiredData == request.POSTLOCATION:
    apiObj.PostLocation()
    
  elif requiredData == request.GETPATIENTLIST:
    apiObj.GetPatientList()
    
  elif requiredData == request.GETPATIENT:
    apiObj.GetPatient(getID)
    
  elif requiredData == request.GETIMAGELIST:
    apiObj.GetImageList()
    
  elif requiredData == request.GETIMAGE:
    apiObj.GetImage(getID)
    
  elif requiredData == request.PUTIMAGE:
    with open(getImageFile, mode='rb') as file: 
      img = file.read()
    apiObj.PutImage()
    
  elif requiredData == request.POSTIMAGE:
    apiObj.PostImage()
  '''

