from utilities import argparser
from modules import map, navigation, pixhawk, position, mission
from modules.MAVLinkThread.mavlinkThread import mavSerial, mavSocket
from threading import Thread
import time
    

if __name__ == "__main__":
    print("*** STARTING ***")
    
    parser = argparser.GetParser()
    args = parser.parse_args()

    '''
    Construct objects
        * Pixhawk - Either serial or UDP connection
        * Position - Either T265 or SITL (Could this just listen to SITL)
        * Mapper - Either blank grid or test enviroment
        * Navigator - Always the same
        * MK:DataHub - Either on/off        
    '''
    pixAddr = (args.pix[0], int(args.pix[1]))

    if args.SITL:
        pixComm = mavSocket.mavSocket( pixAddr )
    else:
        pixComm = mavSerial.mavSerial( pixAddr )

    pixComm.openPort()
    pixObj = pixhawk.pixhawkAbstract( pixComm )

    pixThread = Thread( target = pixObj.loop )
    pixThread.daemon = True
    pixThread.start()

    if args.SITL:
        posComm = mavSocket.mavSocket((args.pix[0], 14552))
        posComm.openPort()
        
        posObj = position.sitlPosition(posComm)

    else:
        posObj = position.position(pixObj)

    posThread = Thread( target = posObj.loop )
    posThread.daemon = True
    posThread.start()

    mapObj = None
    navObj = None
    if args.collision_avoidance:
        if args.SITL:
            mapObj = map.sitlMapper()
        else:
            mapObj = map.mapper()

        navObj = navigation.navigation()

    # Mission progress
    misObj = None
    if args.mission:
        misObj = mission.mission()

    print("*** RUNNING ***")

    ''' 
    Read incoming data and share to relavent objects
        * Position -> Map, Navigation, Pixhawk, MK:DataHub
        * queryPoints -> Map
        * riskValues -> Navigation
        * targetPoint -> Pixhawk
    '''
    try:
        while True:
            startTime = time.time()
            # Get our current location
            pos, rot, conf = posObj.update()

            # Where are we going?
            if args.mission:
                targetPos = misObj.missionProgress(pos)

            if not args.SITL:
                # Tell pixhawk where we are
                pixObj.sendPosition(pos, rot)
                # Update map
                mapObj.update(pos, rot)

            if args.collision_avoidance:
                # Plan next move
                meshPoints = navObj.updatePt1(pos, targetPos)
                pointRisk = mapObj.queryMap(meshPoints)
                goto, heading, risk = navObj.updatePt2(pointRisk)

                print('Goto: {}\t Heading: {:.2f}\t Risk: {:.2f}'.format(goto, heading, risk))

                # Tell pixhawk where to go
                pixObj.directAircraft(goto, heading)
                
            print('Loop time: {:.2f}'.format(time.time()-startTime))

    except KeyboardInterrupt:
        pass

    print("*** STOPPED ***")

    pixObj.stopLoop()
    pixComm.closePort()

    if args.SITL:
        posObj.stopLoop()
        posComm.closePort()

    print("*** BYE ***")
            