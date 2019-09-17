#! .venv/bin/python3

from utilities import argparser
from modules import map, navigation, pixhawk, position, mission, LED, Aircraft_Plotter
from modules.MAVLinkThread.mavlinkThread import mavSerial, mavSocket
from threading import Thread
import time
import traceback
import sys

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
    if args.SITL:
        ledObj = LED.sitlLED()
    else:
        ledObj = LED.LED()

        ledThread = Thread(target=ledObj.loop)
        ledThread.daemon = True
        ledThread.start()
    
    ledObj.setMode(LED.mode.INITIALISE)

    pixAddr = (args.pix[0], int(args.pix[1]))

    if args.SITL:
        pixComm = mavSocket.mavSocket( pixAddr )
    else:
        pixComm = mavSerial.mavSerial( pixAddr )

    pixComm.openPort()
    pixObj = pixhawk.pixhawkAbstract( pixComm )

    pixThread = Thread( target = pixObj.loop, name='pixhawk' )
    pixThread.daemon = True
    pixThread.start()

    while not pixObj.seenHeartbeat and pixComm.isOpen():
        time.sleep(1)

    print('*** PIXHAWK CONNECTED ***')

    if args.SITL:
        posComm = mavSocket.mavSocket((args.pix[0], 14552))
        posComm.openPort()
        posObj = position.sitlPosition(posComm)
    else:
        posObj = position.position(pixObj)

    posThread = Thread( target = posObj.loop, name='position' )
    posThread.daemon = True
    posThread.start()

    if not args.SITL:
        print("*** SET HOME LOCATION ***")
        home_lat = 151269321       # Somewhere in Africa
        home_lon = 16624301        # Somewhere in Africa
        home_alt = 163000

        pixObj.sendSetGlobalOrigin(home_lat, home_lon, home_alt)
        pixObj.sendSetHomePosition(home_lat, home_lon, home_alt)

    mapObj = None

    if args.mapping:
        mapObj = map.mapper()
    elif args.SITL:
        mapObj = map.sitlMapper()

    navObj = None
    if args.collision_avoidance:
        navObj = navigation.navigation()

    # Mission progress
    misObj = None
    if args.mission:
        misObj = mission.mission(pixObj)
    
    
    print("*** RUNNING ***")
    ledObj.setMode(LED.mode.RUNNING)

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
                collision_avoidance, targetPos = misObj.missionProgress(pos)

            if args.mapping:
                # Update map
                mapObj.update(pos, rot)

            if collision_avoidance:
                try:
                    # Plan next move but consider sticking to last move
                    meshPoints = navObj.updatePt1(pos, targetPos)
                    pointRisk = mapObj.queryMap(meshPoints)
                    goto, heading, risk = navObj.updatePt2(pointRisk)

                    #print('Goto: {}\t Heading: {:.2f}\t Risk: {:.2f}'.format(goto, heading, risk))

                    # Tell pixhawk where to go
                    pixObj.directAircraft(goto, heading)
                except ValueError:
                    pass
                Aircraft_Plotter.plot_map(navObj.gotoPoints, navObj.aircraftPosition, mapObj.grid, 1)
            loop_time = time.time() - startTime
            #print('update frequency: {:.2f}'.format(1/loop_time))


            time.sleep(0.2)


            loop_time = time.time() - startTime

    except KeyboardInterrupt:
        pass

    except:
        ledObj.setMode(LED.mode.ERROR)
        traceback.print_exc(file=sys.stdout)

    print("*** STOPPED ***")

    ledObj.clear()

    pixObj.stopLoop()
    pixComm.closePort()

    if args.SITL:
        posObj.stopLoop()
        posComm.closePort()

    print("*** BYE ***")
            
