import numpy as np
import cv2
import math

def plot_map(gotoPoints, position, map, flip = 0):
    if not cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) < 1:
        cv2.namedWindow('rgb_img', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('rgb_img', 100, 100)

    width = map.shape[0]
    height = map.shape[1]
    considered_points = (np.round(gotoPoints[:, 0:2]))
    pos = position
    pts = np.zeros((width,height))
    for i in range(len(considered_points)):
        pts[int(considered_points[i][0]+math.floor(width/2))][int(considered_points[i][1])+math.floor(height/2)] = 1
    pospts = np.zeros((width, height))
    pospts[round(int(pos[0]))+math.floor(width/2)][round(int(pos[1]))+math.floor(height/2)] = 1
    map = np.sum(map, axis=2)
    img = np.asarray([map / np.max(map)]).reshape((width,height))
    img2 = cv2.merge((pts,img,pospts))
    if flip:
        img2 = cv2.flip(img2, 0)
    img2 = cv2.resize(img2, (200,200),interpolation = cv2.INTER_NEAREST)
    cv2.imshow('rgb_img', img2)
    cv2.waitKey(1)