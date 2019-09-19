import numpy as np
import time
class mission:
    patientX = 10.5
    patientY = -7
    #patient pos R, patient pos L, back L, back R, tkOff pos
    missionItems = [[10.6, -6.5, -2],[8.6,-8.4,-1], [1,2,-3], [-0.5,-1,-1], [0,0,-2]]
    #missionItems = [[0, 0, -2],[patientX,patientY,-2]]
    update_rate = 1
    def __init__(self, pixObj):
        self.missionItem = 0
        self.missionItems = np.asarray(self.missionItems)
        self.state = 1
        self.pixObj = pixObj
        self.collision_avoidance = 0
        self.start = 0
        self.landed_pos = 0

    def missionProgress(self, currentPos):
        currentPos = np.asarray(currentPos)
        wpDist = np.linalg.norm(currentPos - self.missionItems[self.missionItem])
        status = 'Unknown'

        # set mode, begin, wait for arm
        if not self.state:
            self.collision_avoidance = 0
            self.missionItem = 0
            status = 'Waiting'

            if time.time() - self.start > self.update_rate:
                self.start = time.time()
                print('beginning mission, setting aircraft to guided')

            if not self.pixObj._mode == 'GUIDED':
                # self.pixObj.setModeGuided()
                time.sleep(0.2)
                return self.collision_avoidance, self.missionItems[self.missionItem], status
            else:
                self.state = 1

        # take off
        if self.state == 1:
            self.collision_avoidance = 0
            self.missionItem = 0

            if not self.pixObj._armed or not self.pixObj._mode == 'GUIDED':
                status = 'Waiting'

                if time.time() - self.start > self.update_rate:
                    self.start = time.time()
                    #self.pixObj.setModeGuided()
                    print("aircraft not armed, cannot take-off")

                return self.collision_avoidance, self.missionItems[self.missionItem], status
            else:

                status = 'Taking Off'
                if time.time() - self.start > self.update_rate:
                    self.start = time.time()
                    print('taking off')
                    
                if abs(currentPos[2]-self.missionItems[self.missionItem,2]) > 0.4:
                    alt = abs(self.missionItems[self.missionItem,2])
                    self.pixObj.setTakeoff(alt)
                    # self.pixObj.setTakeoffLocal(alt)
                    print('*** Send Takeoff ***')

                    return self.collision_avoidance, self.missionItems[self.missionItem], status
                else:
                    self.state = 2

        # follow waypoints
        if self.state == 2:
            self.collision_avoidance = 1
            status = 'Heading to patient'

            if time.time() - self.start > self.update_rate:
                self.start = time.time()
                print('following waypoints, waypoint ',self.missionItem, '\t', self.missionItems[self.missionItem])

            if wpDist < 2:
                self.missionItem += 1
                print('NEXT MISSION ITEM: {}'.format(self.missionItem))

            if self.missionItem == len(self.missionItems):
                self.missionItem -= 1
                self.state = 3
            else:
                return self.collision_avoidance, self.missionItems[self.missionItem], status

        #land
        if self.state == 3:
            self.collision_avoidance = 0
            self.pixObj.setModeLand()
            status = 'Landing at patient'

            if time.time() - self.start > self.update_rate:
                self.start = time.time()
                print('landing aircraft')

            if abs(currentPos[2]) < 0.1:
                self.landed_pos = currentPos
                time.sleep(5)
                self.state = 8
            else:
                return self.collision_avoidance, self.missionItems[self.missionItem], status

        # disarm
        if self.state == 8:
            status = 'Gary going to sleep'

            if time.time() - self.start > self.update_rate:
                self.start = time.time()
                print('end of mission, Gary going to sleep')

            if self.pixObj._armed == True:
                self.pixObj.setArm(0)
            return self.collision_avoidance, self.missionItems[self.missionItem]

        self.pixObj.setModeLand()

        return self.collision_avoidance, self.missionItems[self.missionItem], status

        '''
        #drop
        if self.state == 4:
            if time.time() - self.start > 1:
                self.start = time.time()
                print('dropping payload')
            self.pixObj.drop_payload()
            self.state = 5

        #take off
        if self.state == 5:
            self.collision_avoidance = 0

            if not self.pixObj._armed or not self.pixObj._mode == 'GUIDED':
                if time.time() - self.start > 1:
                    self.start = time.time()
                    print('re-setting guided')

                self.pixObj.setModeGuided()
                #self.pixObj.sendSetHomePosition(0, 0, 0)
                time.sleep(0.2)
                self.pixObj.setArm(1)
                time.sleep(0.2)

                #self.pixObj.sendSetHomePosition(-self.landed_pos[0], -self.landed_pos[1], 0)
                time.sleep(0.2)

                return self.collision_avoidance, self.missionItems[self.missionItem]

            if abs(currentPos[2] - self.missionItems[self.missionItem, 2]) > 0.4:
                if time.time() - self.start > 1:
                    self.start = time.time()
                    print('takeoff')
                self.pixObj.setTakeoff(abs(self.missionItems[self.missionItem,2]))
                return self.collision_avoidance, self.missionItems[self.missionItem]
            else:
                self.state = 6

        #follow waypoints
        if self.state == 6:
            self.collision_avoidance = 1
            if time.time() - self.start > 1:
                self.start = time.time()
                print('following waypoints, waypoint ', self.missionItem, '\t', self.missionItems[self.missionItem])
            if wpDist < 2:
                self.missionItem -= 1
                print('NEXT MISSION ITEM: {}'.format(self.missionItem))
            if self.missionItem == -1:
                self.state = 7
            else:
                return self.collision_avoidance, self.missionItems[self.missionItem]

        # land
        if self.state == 7:
            self.collision_avoidance = 0
            if time.time() - self.start > 1:
                self.start = time.time()
                print('landing aircraft')
            self.pixObj.setModeLand()
            if currentPos[2] < 0.1:
                self.state = 8
                time.sleep(5)
            else:
                return self.collision_avoidance, self.missionItems[self.missionItem]
        '''




