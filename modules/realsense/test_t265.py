import t265

t265Obj = t265.rs_t265()

with t265Obj:
    for i in range(1000):
        pos, quat, conf = t265Obj.getFrame()
        print(i, pos, conf)