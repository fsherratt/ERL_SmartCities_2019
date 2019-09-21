import numpy as np
import time
class mission:
    patientX = 11
    patientY = -8

    missionItems = [[patientX,patientY,-2], [0, 0, -2]]
    update_rate = 1

    def __init__(self, pixObj):
        self.missionItem = 0
        self.missionItems = np.asarray(self.missionItems)
        self.pixObj = pixObj

        self.state = 0

        self.collision_avoidance = False
        self.status = 'Unknown'
        self.gotoPoint = [0,0,0]

        self.waitTime = 0.5

    def missionProgress(self, currentPos):
        currentPos = np.asarray(currentPos)
        wpDist = np.linalg.norm(currentPos - self.missionItems[self.missionItem])

        if self.state == 0:
            self.collision_avoidance = False
            self.status = 'Initialising'
            self.gotoPoint = [0,0,0]

            self.pixObj.close_payload()
            self.pixObj.setModePosHold()

            if self.pixObj.mode == 'POSHOLD':
                self.state = 1
            else:
                print('Set mode to PosHold')
                time.sleep(self.waitTime)
            
        elif self.state == 1:
            self.collision_avoidance = False
            self.status = 'Initialising'
            self.gotoPoint = [0,0,0]

            if self.pixObj.armed:
                self.state = 2
            else:
                print('Waiting for arm')
                time.sleep(self.waitTime)

        elif self.state == 2:
            self.collision_avoidance = False
            self.status = 'Takeoff'
            self.gotoPoint = [0,0,0]
            
            self.pixObj.setModeGuided()
            if self.pixObj.mode == 'GUIDED':
                self.state = 3
            else:
                print('Set mode to Guided')
                time.sleep(self.waitTime)

        elif self.state == 3:   
            self.collision_avoidance = False
            self.status = 'Takeoff'
            self.gotoPoint = [0,0,0] #think this will make it land as soon as its taken off

            self.pixObj.setTakeoff(1.5) # changed alt to 1.5 from 1

            if currentPos[2] < -1:
                self.state = 4    
            else:
                time.sleep(self.waitTime)       

        elif self.state == 4:
            self.collision_avoidance = True
            self.status = 'Flying to patient'
           
            # Fly Somewhere
            self.gotoPoint = self.missionItems[0]

            if wpDist < 0.4:
                self.state = 5

        elif self.state == 5:
            self.collision_avoidance = False
            self.status = 'Landing'
            self.gotoPoint = [0,0,0]

            print('Set Land')
            self.pixObj.setModeLand()

            if self.pixObj.mode == 'LAND':
                self.state = 6
            else:
                print('Set mode to land')
                time.sleep(self.waitTime)

        elif self.state == 6:
            self.collision_avoidance = False
            self.status = 'Landing'
            self.gotoPoint = [0,0,0]

            if self.pixObj.armed:
                time.sleep(self.waitTime)
            else:
                self.state = 7
                print('Landed')

        elif self.state == 7:
            self.collision_avoidance = False
            self.status = 'Dropping Payload'
            self.gotoPoint = [0,0,0]

            self.pixObj.drop_payload()
            time.sleep(self.waitTime)
            self.state = 8

        elif self.state == 8:
            self.collision_avoidance = False
            self.status = 'Takeoff'
            self.gotoPoint = [0,0,0]

            self.pixObj.setModePosHold()
            if self.pixObj.mode == 'POSHOLD':
                self.state = 9
            else:
                print('Set mode to PosHold')
                time.sleep(self.waitTime)

        elif self.state == 9:
            self.collision_avoidance = False
            self.status = 'Takeoff'
            self.gotoPoint = [0,0,0]

            self.pixObj.setArm(True)
            self.pixObj.setGotoOffset( currentPos )
            if self.pixObj.armed:
                self.state = 10
            else:
                time.sleep(self.waitTime)

        elif self.state == 10:
            self.collision_avoidance = False
            self.status = 'Takeoff'
            self.gotoPoint = [0,0,0]

            print('Guided')
            self.pixObj.setModeGuided()
            
            if self.pixObj.mode == 'GUIDED':
                self.state = 11
            else:
                print('Set mode to Guided')
                time.sleep(self.waitTime)
        
        elif self.state == 11:
            self.collision_avoidance = False
            self.status = 'Takeoff'
            self.gotoPoint = [0,0,0]

            self.pixObj.setTakeoff(1.5) # same again

            if currentPos[2] < -1:
                self.state == 12
            else:
                time.sleep(self.waitTime)

        elif self.state == 12:
            self.collision_avoidance = True
            self.status = 'Flying to patient'
           
            # Fly Somewhere
            self.gotoPoint = self.missionItems[1]

            if wpDist < 0.4:
                self.state = 13

        elif self.state == 13:
            self.collision_avoidance = False
            self.status = 'Landing'
            self.gotoPoint = [0,0,0]

            if self.pixObj.mode == 'LAND':
                self.state = 14
            else:
                print('Set mode to land')
                time.sleep(self.waitTime)

        elif self.state == 14:
            self.collision_avoidance = False
            self.status = 'Landing'
            self.gotoPoint = [0,0,0]

            if not self.pixObj.armed:
                self.state = 15
            else:
                time.sleep(self.waitTime)
        
        elif self.state == 15:
            self.collision_avoidance = False
            self.status = 'Done'
            self.gotoPoint = [0,0,0]

            time.sleep(self.waitTime)

        # Enable collision avoidance, goto point, status
        return self.collision_avoidance, self.gotoPoint, self.status
