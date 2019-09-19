#! .venv/bin/python3

from utilities import argparser
from modules import map, navigation, pixhawk, position, mission, LED, telemetry, Aircraft_Plotter
from modules.MAVLinkThread.mavlinkThread import mavSerial, mavSocket
from modules.realsense import d435
from threading import Thread
import time
import traceback
import sys
import cv2

import numpy as np
np.set_printoptions(precision=3, suppress=True)

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
        ledThread = Thread(target=ledObj.loop, name='LED')
        ledThread.daemon = True
        ledThread.start()
    
    ledObj.setMode(LED.mode.INITIALISE)

    if args.telemetry:
        telemObj = telemetry.airTelemetry()
        telemObj.start()

    pixAddr = (args.pix[0], int(args.pix[1]))

    if args.SITL:
        pixComm = mavSocket.mavSocket( pixAddr )
    else:
        pixComm = mavSerial.mavSerial( pixAddr )

    pixComm.openPort()
    pixObj = pixhawk.pixhawkAbstract( pixComm )

    pixThread = Thread( target = pixObj.loop, name='pixhawk' )
    # pixThread.daemon = True
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

    print("*** SET HOME LOCATION ***")

    pixObj.sendSetGlobalOrigin()
    pixObj.sendSetHomePosition()

    mapObj = None

    mapObj = None
    if args.SITL:
        mapObj = map.sitlMapper()
    elif args.mapping:
        mapObj = map.mapper()
        d435Obj = d435.rs_d435(framerate=30, width=480, height=270)
        d435Obj.openConnection()

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
        mission_collision_avoidance = False
        while True:
            startTime = time.time()

            # Get our current location
            pos, rot, conf = posObj.update()
            if args.telemetry:
                telemObj.sendData(telemetry.DataType.TELEM_POSITION, pos)

            # Where are we going?
            if args.mission:
                mission_collision_avoidance, targetPos, status = misObj.missionProgress(pos)

                if args.telemetry:
                    telemObj.sendData(telemetry.DataType.TELEM_STATUS, status)

            if args.mapping:
                # Update map
                frame, rgbImg = d435Obj.getFrame()
                points = d435Obj.deproject_frame(frame)
                mapObj.update(points, pos, rot)

                if args.telemetry:
                    depth = cv2.applyColorMap(cv2.convertScaleAbs(frame, alpha=0.03), cv2.COLORMAP_JET)
                    telemObj.sendImage(telemetry.DataType.TELEM_DEPTH_FRAME, depth)

                    telemObj.sendImage(telemetry.DataType.TELEM_RGB_IMAGE, rgbImg)

            if mission_collision_avoidance:
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
                # Aircraft_Plotter.plot_map(navObj.gotoPoints, navObj.aircraftPosition, mapObj.grid, 1)
            
            
            time.sleep(0.2)
            loop_time = time.time() - startTime
            print('update frequency: {:.2f}'.format(1/loop_time))
            # print('pos {}\t rot {}\t conf {}'.format(pos, rot.as_euler('xyz', degrees=True), conf))


    except KeyboardInterrupt:
        if args.mapping:
            print('*** Save Map ***')
            mapObj.saveToMatlab('map.mat')

    except:
        traceback.print_exc(file=sys.stdout)
        ledObj.setMode(LED.mode.ERROR)
        traceback.print_exc(file=sys.stdout)

    print("*** STOPPED ***")

    ledObj.clear()

    pixObj.stopLoop()
    pixThread.join()
    pixComm.closePort()

    if args.mapping:
        d435Obj.closeConnection()

    if args.SITL:
        posObj.stopLoop()
        posComm.closePort()

    if args.telemetry:
        telemObj.stop()
        
    ledObj.close()

    print("*** BYE ***")
