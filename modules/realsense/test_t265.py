import t265

t265Obj = t265.rs_t265()

with t265Obj:
    while True:
        pos, eul, conf = t265Obj.getFrame()
        # print(i, pos, conf)

        pos, eul = t265Obj.correctOffset( pos, eul )

        print(pos)