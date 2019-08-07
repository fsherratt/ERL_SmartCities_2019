import argparse

def GetParser():
    parser = argparse.ArgumentParser(
            description = 'SciRoc Episode 12 argument parser' )

    parser.add_argument( '--pix', '-P',
                     type = str,
                     help = 'Pixhawk Serial port',
                     metavar = ('PORT', 'BAUD'),
                     default = None,
                     nargs = 2,
                     required = True)

    parser.add_argument( '--gnd', '-G',
                     type = str,
                     help = 'Ground Station Serial port',
                     metavar = ('PORT', 'BAUD'),
                     default = None,
                     nargs = 2 )

    parser.add_argument( '--disp', '-V',
                     help = 'Enable displaying of camera image',
                     default = None,
                     action = "store_true" )

    parser.add_argument('--save', '-S',
                    help='Save images from the camera',
                    default=None,
                    action="store_true")

    return parser