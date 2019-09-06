import argparse

def GetParser():
    parser = argparse.ArgumentParser(
            description = 'SciRoc Episode 12 argument parser' )

    parser.add_argument( '--pix', '-P',
                        type = str,
                        help = 'Pixhawk address - for SITL UDP otherwise serial',
                        metavar = ('ADDR', 'PORT/BAUD'),
                        default = None,
                        nargs = 2 )

    parser.add_argument( '--SITL', '-s',
                        help = 'Enable pixhawk SITL',
                        default = None,
                        action = "store_true",
                        required = False  )

    parser.add_argument( '--collision-avoidance', '-c',
                        help = 'Enable collision avoidance',
                        default = None,
                        action = "store_true",
                        required=False)

    parser.add_argument( '--mission', '-m',
                        help = 'Enable mission progress',
                        default = None,
                        action = "store_true",
                        required=False)

    return parser