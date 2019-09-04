from utilities import argparser
from modules import map, navigation, pixhawk, position
from modules.MAVLinkThread.mavlinkThread import mavSerial, mavSocket
from threading import Thread

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
        posComm = mavSocket.mavSocket((args.pix[0], int(args.pix[1])+1))
        posComm.openPort()
        
        posObj = position.sitlPosition(posComm)

        posThread = Thread( target = posObj.loop )
        posThread.daemon = True
        posThread.start()

    else:
        posObj = position.position()

    mapObj = map.mapper( args.SITL )
    navObj = navigation.navigation()

    print("*** RUNNING ***")

    ''' 
    Read incoming data and share to relavent objects
        * Position -> Map, Navigation, Pixhawk, MK:DataHub
        * queryPoints -> Map
        * riskValues -> Navigation
        * targetPoint -> Pixhawk
    '''
    try:
        targetPos = [10,0,0]
        while True:
            # Get our current location
            pos, rot, conf = posObj.update()

            if not args.SITL:
                # Tell pixhawk where we are
                pixObj.sendPosition(pos, rot)
                # Update map
                mapObj.update(pos, rot)

            # Plan next move
            meshPoints = navObj.updatePt1(pos, targetPos)
            pointRisk = mapObj.queryMap(meshPoints)
            goto, yaw, risk = navObj.updatePt2(pointRisk)

            # Tell pixhawk where to go
            pixObj.sendGoto(goto, yaw)

    except KeyboardInterrupt:
        pass

    print("*** STOPPED ***")

    pixObj.stopLoop()
    pixComm.closePort()

    if args.SITL:
        posObj.stopLoop()
        posComm.closePort()

    print("*** BYE ***")
            