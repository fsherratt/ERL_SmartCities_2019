import map

mapObj = map.mapper()

try:
    with mapObj:
        mapObj.loop()

except KeyboardInterrupt:
    pass