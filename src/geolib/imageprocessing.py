import itertools
import math

import cv2
import numpy as np


def trigArea(trig):
    trig = trig[0]

    def distance(p1, p2):
        x, y = p1 - p2
        return math.sqrt(x * x + y * y)

    distances = []
    for a, b in itertools.combinations(trig, 2):
        distances.append(distance(a, b))
    # Heron's Formula
    p = sum(distances) / 2
    a, b, c = distances
    # print(p,a,b,c)
    return math.sqrt(p * (p - a) * (p - b) * (p - c))


def color_from_path(node, image):
    path = node.data.copy()

    # shaped = np.reshape(path, (2, -1))
    # print(path)
    shaped = path

    ymax, xmax, _ = image.shape

    roi_x = min(xmax, np.amax(shaped[:, 0]))
    roi_x2 = min(xmax, np.amin(shaped[:, 0]))
    roi_y = min(ymax, np.amax(shaped[:, 1]))
    roi_y2 = min(ymax, np.amin(shaped[:, 1]))

    # print('roi',roi_x, roi_x2, roi_y, roi_y2)
    image2 = image[roi_y2:roi_y, roi_x2:roi_x]
    # print('shape_new', image2.shape, path, roi_x2, roi_x, roi_y2, roi_y)
    # print(shaped[:, 0])
    # print(shaped[:, 1])
    path[:, 0] -= roi_x2
    path[:, 1] -= roi_y2
    # print(path)
    if min(image2.shape) == 0:
        # print('shape_new', image2.shape, path, roi_x2, roi_x, roi_y2, roi_y)
        # print(shaped[:,0])
        # print(shaped[:,1])
        # print(path)
        return (255, 255, 255)
    # path = [path]
    # mask = np.zeros(shape=(image2.shape[0],image2.shape[1]),dtype=np.uint8)
    mask = np.zeros(shape=(image2.shape[0], image2.shape[1]), dtype=np.uint8)
    # print(mask.shape)
    drawn = cv2.fillPoly(mask, [path], (255))
    # cv2.polylines(mask, path, True, (255,))
    # print(mask.shape)
    # print(image.shape)
    img = cv2.bitwise_and(image2, image2, mask=mask)
    b, g, r = cv2.split(img)
    area = 0
    if not 'area' in node.attrs:
        # print(path)
        area = trigArea(path)
        node.attrs['area'] = area
    else:
        area = node.attrs['area']

    def avgnonzero(x):

        # nz = x[x.nonzero()]
        # if len(nz) > 0:
        #    return np.sum(nz) / len(nz)
        # else:
        #    return 0
        if area != 0:
            return np.sum(x) / area
        else:
            return 0

    #print(np.sum(img,axis=(0,1,2)) )
    newcolor = tuple(int(avgnonzero(x)) for x in [r, g, b])
    return newcolor
