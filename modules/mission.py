import numpy as np
import time
import modules.pixhawk
class mission:
    missionItems = [[-15, -15, -5], [15, -15, -5], [15, 15, -5], [-15, 15, -5]]
    #missionItems = [[-5, -5, -5], [5, -5, -5], [5, 5, -5], [-5, 5, -5]]
    def __init__(self, pixObj):
        self.missionItem = 0
        self.missionItems = np.asarray(self.missionItems)
        self.state = 0
        self.pixObj = pixObj
        self.collision_avoidance = 0
        self.start = 0
        self.landed_pos = 0

    def missionProgress(self, currentPos):
        currentPos = np.asarray(currentPos)
        wpDist = np.linalg.norm(currentPos - self.missionItems[self.missionItem])

        # arm
        if not self.state:
            if time.time() - self.start > 1:
                self.start = time.time()
                print('beginning mission, setting aircraft to guided')
            if not self.pixObj._mode == 'GUIDED':
                self.pixObj.setModeGuided()
                self.collision_avoidance = 0
                self.missionItem = 0
                return self.collision_avoidance, self.missionItems[self.missionItem]
            else:
                self.state = 1

        # take off
        if self.state == 1:
            if not self.pixObj._armed:
                if time.time() - self.start > 1:
                    self.start = time.time()
                    print("aircraft not armed, cannot take-off")
                return self.collision_avoidance, self.missionItems[self.missionItem]
            else:
                if time.time() - self.start > 1:
                    self.start = time.time()
                    print('taking off')
                if abs(currentPos[2]-self.missionItems[self.missionItem,2]) > 0.4:
                    self.pixObj.setModeGuided()
                    self.pixObj.setTakeoff(abs(self.missionItems[self.missionItem,2]))
                    self.collision_avoidance = 0
                    self.missionItem = 0
                    return self.collision_avoidance, self.missionItems[self.missionItem]
                else:
                    self.state = 2

        # follow waypoints
        if self.state == 2:
            if time.time() - self.start > 1:
                self.start = time.time()
                print('following waypoints, waypoint ',self.missionItem, '\t', self.missionItems[self.missionItem])
            self.collision_avoidance = 1
            if wpDist < 2:
                self.missionItem += 1
                print('NEXT MISSION ITEM: {}'.format(self.missionItem))
            if self.missionItem == len(self.missionItems):
                self.missionItem -= 1
                self.state = 3
            else:
                return self.collision_avoidance, self.missionItems[self.missionItem]

        #land
        if self.state == 3:
            self.collision_avoidance = 0
            self.pixObj.setModeLand()
            if time.time() - self.start > 1:
                self.start = time.time()
                print('landing aircraft')
            if abs(currentPos[2]) < 0.1:
                time.sleep(5)
                self.state = 5
                self.landed_pos= currentPos
            else:
                return self.collision_avoidance, self.missionItems[self.missionItem]
        #drop
        if self.state == 4:
            if time.time() - self.start > 1:
                self.start = time.time()
                print('dropping payload')
            self.pixObj.drop_payload()
            self.state = 5

        #take off
        if self.state == 5:

            if not self.pixObj._armed or not self.pixObj._mode == 'GUIDED':
                if time.time() - self.start > 1:
                    self.start = time.time()
                    print('re-setting guided')
                self.pixObj.setModeGuided()
                self.pixObj.setArm(1)
                self.collision_avoidance = 0
                return self.collision_avoidance, self.missionItems[self.missionItem]
            if abs(currentPos[2] - self.missionItems[self.missionItem, 2]) > 0.4:
                if time.time() - self.start > 1:
                    self.start = time.time()
                    print('takeoff')
                self.collision_avoidance = 0
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

        #disarm
        if self.state == 8:
            if time.time() - self.start > 1:
                self.start = time.time()
                print('end of mission, Gary going to sleep')
            if self.pixObj._armed == True:
                self.pixObj.setArm(0)
            return self.collision_avoidance, self.missionItems[self.missionItem]

        self.pixObj.setModeLand()
        return self.collision_avoidance, self.missionItems[self.missionItem]



