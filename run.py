from utilities import argparser
from modules import map, navigation, pixhawk, position

if __name__ == "__main__":
    parser = argparser.GetParser()
    args = parser.parse_args()

    if args.SITL:
        print('SITL Enabled')

    '''
    Construct objects
        * Pixhawk - Either serial or UDP connection
        * Position - Either T265 or SITL (Could this just listen to SITL)
        * Mapper - Either blank grid or test enviroment
        * Navigator - Always the same
        * MK:DataHub - Either on/off        
    '''

    while True:
        pass
        ''' 
        Read incoming data and share to relavent objects
            * Position -> Map, Navigation, Pixhawk, MK:DataHub
            * queryPoints -> Map
            * riskValues -> Navigation
            * targetPoint -> Pixhawk
        '''