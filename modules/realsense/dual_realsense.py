import d435
import t265

d435Obj = d435.rs_d435( framerate = 30 )
t265Obj = t265.rs_t265()

with d435Obj, t265Obj:
    while True:
        depthFrame = d435Obj.getFrame()
        pos, eul, conf = t265Obj.getFrame()

        pos, eul = t265Obj.correctOffset( pos, eul )

        breakpoint()
        pass