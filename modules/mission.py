import numpy as np

class mission:
    missionItems = [[-15,-15,-5], [15,-15,-5], [15, 15,-5], [-15, 15,-5]]

    def __init__(self):
        self.missionItem = 0
        self.missionItems = np.asarray(self.missionItems)

    def missionProgress(self, currentPos):
        currentPos = np.asarray(currentPos)
        wpDist =  np.linalg.norm(currentPos - self.missionItems[self.missionItem])

        if wpDist < 2:
            self.missionItem += 1

            if self.missionItem >= len(self.missionItems):
                self.missionItem = 0

            print('NEXT MISSION ITEM: {}'.format(self.missionItem))

        return self.missionItems[self.missionItem]
