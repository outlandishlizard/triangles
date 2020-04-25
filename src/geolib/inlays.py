import itertools
import math
import random

import networkx as nx

from .helpers import *


class IDNode(object):
    ctr = 0

    def __init__(self, data):
        self.ctr = IDNode.ctr
        IDNode.ctr += 1
        self.data = data
        self.attrs = {}

    def __hash__(self):
        return self.ctr

    def cmp(self, other):
        if type(self) == type(other):
            return True
        else:
            return False

    def __eq__(self, other):
        return self.cmp(other)

    def __lt__(self, other):
        return self.cmp(other)

    def __gt__(self, other):
        return self.cmp(other)

    def __ge__(self, other):
        return self.cmp(other)

    def __le__(self, other):
        return self.cmp(other)

    def __ne__(self, other):
        return self.cmp(other)


def randomPoint(l, w):
    x = random.random() * l
    y = random.random() * w
    return np.array([x, y], dtype=np.int32)


def randomTriangle(l, w):
    tri = IDNode(np.array([randomPoint(l, w), randomPoint(l, w), randomPoint(l, w)], dtype=np.int32))
    while isTooSmall(tri):
        tri = IDNode(np.array([randomPoint(l, w), randomPoint(l, w), randomPoint(l, w)], dtype=np.int32))
    return tri


def fillingTiled(l, w, n=4):
    mid_l = l / n
    mid_w = w / n
    for i in range(n):
        y_1 = mid_w * i
        y_2 = y_1 + mid_w
        for j in range(n):
            x_1 = mid_l * j
            x_2 = x_1 + mid_l
            yield np.array([np.array(pair) for pair in [(x_1, y_1), (x_2, y_1), (x_1, y_2)]], dtype=np.int32)
            yield np.array([np.array(pair) for pair in [(x_1, y_2), (x_2, y_1), (x_2, y_2)]], dtype=np.int32)


def fillingTriangle(l, w):
    tri = np.array([np.array(x) for x in [[1, l / 2], [w, 1], [l, w]]], dtype=np.int32)
    # print(tri)
    return tri

def distance(p1, p2):
    x, y = p1 - p2
    return math.sqrt(x * x + y * y)


def trigArea(distances):
    # Heron's Formula
    p = sum(distances) / 2
    a, b, c = distances
    return math.sqrt(p * (p - a) * (p - b) * (p - c))


def trigAngles(distances):
    a, b, c = distances
    angle_1 = math.degrees(math.acos((b * b + c * c - a * a) / (2 * b * c)))
    angle_2 = math.degrees(math.acos((a * a + c * c - b * b) / (2 * a * c)))
    angle_3 = 180 - angle_1 - angle_2

    return angle_1, angle_2, angle_3


def isTooSmall(trig_node, area_limit=250, dist_limit=10, angle_limit=15):
    trig = trig_node.data
    distances = []
    for a, b in itertools.combinations(trig, 2):
        distances.append(math.hypot(*a - b))

    if 'area' not in trig_node.attrs:
        area = trigArea(distances)
        trig_node.attrs['area'] = area
    else:
        area = trig_node.attrs['area']
    if area < area_limit:
        # print("area limit hit")
        return True
    for dist in distances:
        if dist < dist_limit:
            # print("point distance limit hit")
            return True

    angles = trigAngles(distances)
    for angle in angles:
        # print('a',angle)
        if angle < angle_limit:
            #print("angle limit hit", angle)
            return True

    return False


def getDirection(p1, p2):
    d = p2 - p1
    return d


def getPointTowards(fr, to, scale=0.1):
    direct = getDirection(fr, to)
    return fr + (direct * scale)


def inlayTriangle(trig):
    centroid = sum(trig.data) / len(trig.data)
    inlaid = np.array([getPointTowards(pt, centroid) for pt in trig.data], dtype=np.int32)
    inlaid = IDNode(inlaid)
    return inlaid, []


def inlayCentroid(trig):
    centroid = sum(trig.data) / len(trig.data)
    rets = []
    for a, b in itertools.combinations(trig.data, 2):
        rets.append(IDNode(np.array([a, b, centroid], dtype=np.int32)))
    return rets[0], rets[1:]


def inlayTriforce(trig_node):
    trig = trig_node.data
    a = (trig[0] + trig[1]) / 2
    b = (trig[1] + trig[2]) / 2
    c = (trig[2] + trig[0]) / 2
    center = IDNode(np.array([a, b, c], dtype=np.int32))
    top = IDNode(np.array([trig[0], a, c], dtype=np.int32))
    left = IDNode(np.array([trig[1], a, b], dtype=np.int32))
    right = IDNode(np.array([trig[2], b, c], dtype=np.int32))
    if 'area' in trig_node.attrs:
        for node in [center, top, left, right]:
            node.attrs['area'] = trig_node.attrs['area'] / 4
    return center, [top, left, right]


def subdivideLine(line, n):
    pts = []
    a, b = line
    for i in range(1, n):
        pt = getPointTowards(a, b, scale=i / n)
        pts.append(pt)
    # print(pts)
    return pts


def getMidpoint(a, b):
    return getPointTowards(a, b, scale=.5)


def inlayRays_deterministic(trig, n=None):
    if n is None:
        n = 5

    # print(trig)
    rets = []
    origin_idx = 0
    origin = trig[origin_idx]
    # print(origin_idx)
    others = np.append(trig[:origin_idx], trig[origin_idx + 1:], axis=0)
    # print(others)
    points = subdivideLine(others, n)
    points = [others[0]] + points
    for i in range(len(points)):
        cur = points[i]
        try:
            nxt = points[i + 1]
        except IndexError:
            nxt = others[-1]
        node = IDNode(np.array([origin, cur, nxt]), dtype=np.int32)
        if 'area' in trig.attrs:
            node.attrs['area'] = trig.attrs['area'] / n
        rets.append(node)
    # print(rets)
    # print(len(rets))
    return rets[0], rets[1:]


def inlayRays(trig, n=None):
    if n is None:
        n = random.randint(1, 7)

    # print(trig)
    rets = []
    origin_idx = random.randint(0, len(trig.data) - 1)
    # print(trig.data,origin_idx)
    origin = trig.data[origin_idx]
    # print(origin_idx)
    others = np.append(trig.data[:origin_idx], trig.data[origin_idx + 1:], axis=0)
    # print(others)
    points = subdivideLine(others, n)
    points = [others[0]] + points
    for i in range(len(points)):
        cur = points[i]
        try:
            nxt = points[i + 1]
        except IndexError:
            nxt = others[-1]
        node = IDNode(np.array([origin, cur, nxt], dtype=np.int32))
        if 'area' in trig.attrs:
            node.attrs['area'] = trig.attrs['area'] / n
        rets.append(node)
    # print(rets)
    # print(len(rets))
    return rets[0], rets[1:]


def doRandomInlays(trig, n):
    #print('Entering inlay',trig, trig.data)
    if trig.__class__ != IDNode:
        trig = IDNode(trig)
    gr = nx.DiGraph()
    gr.add_node(trig)
    fns = [inlayTriangle, inlayTriforce, inlayRays, inlayCentroid]
    # fns = [inlayCentroid]
    if n <= 0:
        return [], gr
    if isTooSmall(trig, angle_limit=5):
        # print('Too small, aborting at n:', n)
        return [], gr

    # inlay = trig.data
    ret = []
    fn = fns[random.randint(0, len(fns) - 1)]
    main, extras = fn(trig)
    # main = IDNode(main)
    # extras = [IDNode(extra) for extra in extras]
    gr.add_node(main)
    gr.add_nodes_from(extras)

    for node in [main] + extras:
        gr.add_edge(trig, node)

    ret += [main]
    ret += extras
    for sub in [main] + extras:
        roots, subgraph = doRandomInlays(sub, n - 1)
        gr.add_nodes_from(subgraph)
        gr.add_edges_from(subgraph.edges)
        for root in roots:
            gr.add_edge(sub, root)

    return [main] + extras, gr


def outlayReflect(trig):
    # Keep two points, reflect 1 across them.
    p1, p2, p3 = trig.data
    mid = getMidpoint(p1, p2)
    reflected = mid - (p3 - mid)
    new = IDNode(np.array([p1, p2, reflected], dtype=np.int32))
    gr = nx.DiGraph()
    gr.add_node(new)
    return [new], gr


def strategy_bydepth(node, n, fns):
    # This doesn't produce a perfectly symmetrical result because some functions themselves contain randomness
    # For example, inlayRays picks n and the starting vertex at random. This could be fixed by using a seed
    # derived from some shared randomness  and the current depth.
    # print(n, n % len(fns))
    return fns[n % len(fns)]


def strategy_samerandom(node, n, fns, seed):
    # Produces a very similar result to bydepth, but picks the next function to apply at a given depth at "random" (seed
    # is derived from depth and a static seed passed in) rather than by depth % len(functions).
    full_seed = str(n) + ':' + str(seed)
    r = random.Random(full_seed)
    return r.sample(fns, 1)[0]


def strategy_random(node, n, fns):
    return random.sample(fns, 1)[0]


all_fns = [inlayTriforce, inlayTriangle, inlayCentroid, inlayRays]


def doInlays(trig, strategy, n=100, strategy_args=None):
    if n <= 0:
        return [], nx.DiGraph()
    if trig.__class__ != IDNode:
        trig = IDNode(trig)
    if strategy_args is None:
        strategy_args = []

    if isTooSmall(trig, angle_limit=3):
        # print('Too small, aborting at n:', n)
        return [], nx.DiGraph()

    gr = nx.DiGraph()
    gr.add_node(trig)

    ret = []

    all_strategy_args = [trig, n] + strategy_args
    fn = strategy(*all_strategy_args)
    # print(fn)
    main, extras = fn(trig)
    # main = IDNode(main)
    # extras = [IDNode(extra) for extra in extras]
    gr.add_node(main)
    gr.add_nodes_from(extras)
    for node in [main] + extras:
        gr.add_edge(trig, node)

    ret += [main]
    ret += extras
    for sub in [main] + extras:
        roots, subgraph = doInlays(sub, strategy, n=n - 1, strategy_args=strategy_args)
        gr.add_nodes_from(subgraph)
        gr.add_edges_from(subgraph.edges)
        for root in roots:
            gr.add_edge(sub, root)

    return [main] + extras, gr
