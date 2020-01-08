import itertools
import random

import math
import networkx as nx

from src.helpers import *


class IDNode(object):
    ctr = 0

    def __init__(self, data):
        self.ctr = IDNode.ctr
        IDNode.ctr += 1
        self.data = data
        self.attrs = {}

    def __hash__(self):
        return self.ctr.__hash__()

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
    return np.array([x, y])


def randomTriangle(l, w):
    tri = np.array([randomPoint(l, w), randomPoint(l, w), randomPoint(l, w)])
    while isTooSmall(tri):
        tri = np.array([randomPoint(l, w), randomPoint(l, w), randomPoint(l, w)])
    return tri


def distance(p1, p2):
    x, y = p1 - p2
    return math.sqrt(x * x + y * y)


def trigArea(trig):
    # Heron's Formula
    lines = []
    for a, b in itertools.combinations(trig, 2):
        lines.append(distance(a, b))
    p = sum(lines) / 2
    a, b, c = lines
    return math.sqrt(p * (p - a) * (p - b) * (p - c))


def trigAngles(trig):
    lines = []
    for a, b in itertools.combinations(trig, 2):
        lines.append(distance(a, b))
    a, b, c = lines
    angle_1 = math.degrees(math.acos((b * b + c * c - a * a) / (2 * b * c)))
    angle_2 = math.degrees(math.acos((a * a + c * c - b * b) / (2 * a * c)))
    angle_3 = 180 - angle_1 - angle_2

    return angle_1, angle_2, angle_3


def isTooSmall(trig, area_limit=250, dist_limit=10, angle_limit=15):
    if trigArea(trig) < area_limit:
        print("area limit hit")
        return True
    for a, b in itertools.combinations(trig, 2):
        dist = distance(a, b)
        # print(dist)
        if dist < dist_limit:
            print("point distance limit hit")
            return True

    angles = trigAngles(trig)
    for angle in angles:
        # print('a',angle)
        if angle < angle_limit:
            print("angle limit hit", angle)
            return True

    return False


def getDirection(p1, p2):
    d = p2 - p1
    return d


def getPointTowards(fr, to, scale=0.1):
    direct = getDirection(fr, to)
    return fr + (direct * scale)


def inlayTriangle(trig):
    trig = to_np(trig)
    centroid = sum(trig) / len(trig)
    inlaid = np.array([getPointTowards(pt, centroid) for pt in trig])
    return inlaid, []


def inlayCentroid(trig):
    trig = to_np(trig)
    centroid = sum(trig) / len(trig)
    rets = []
    for a, b in itertools.combinations(trig, 2):
        rets.append(np.array([a, b, centroid]))
    return rets[0], rets[1:]


def inlayTriforce(trig):
    trig = to_np(trig)
    a = (trig[0] + trig[1]) / 2
    b = (trig[1] + trig[2]) / 2
    c = (trig[2] + trig[0]) / 2
    center = np.array([a, b, c])
    top = np.array([trig[0], a, c])
    left = np.array([trig[1], a, b])
    right = np.array([trig[2], b, c])

    return center, [top, left, right]


def subdivideLine(line, n):
    pts = []
    a, b = line
    for i in range(1, n):
        pt = getPointTowards(a, b, scale=i / n)
        pts.append(pt)
    # print(pts)
    return pts


def inlayRays_deterministic(trig, n=None):
    if n is None:
        n = 5
    trig = to_np(trig)
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
        rets.append(np.array([origin, cur, nxt]))
    # print(rets)
    # print(len(rets))
    return rets[0], rets[1:]


def inlayRays(trig, n=None):
    if n is None:
        n = random.randint(0, 7)
    trig = to_np(trig)
    # print(trig)
    rets = []
    origin_idx = random.randint(0, len(trig) - 1)
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
        rets.append(np.array([origin, cur, nxt]))
    # print(rets)
    # print(len(rets))
    return rets[0], rets[1:]


def doRandomInlays(trig, n):
    if trig.__class__ != IDNode:
        trig = IDNode(trig)
    gr = nx.DiGraph()
    gr.add_node(trig)
    fns = [inlayTriangle, inlayTriforce, inlayRays, inlayCentroid]
    # fns = [inlayCentroid]
    if n <= 0:
        return [], gr
    if isTooSmall(trig.data, angle_limit=5):
        print('Too small, aborting at n:', n)
        return [], gr

    inlay = trig.data
    ret = []
    fn = fns[random.randint(0, len(fns) - 1)]
    main, extras = fn(inlay)
    main = IDNode(main)
    extras = [IDNode(extra) for extra in extras]
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


def strategy_bydepth(node, n, fns):
    # This doesn't produce a perfectly symmetrical result because some functions themselves contain randomness
    # For example, inlayRays picks n and the starting vertex at random. This could be fixed by using a seed
    # derived from some shared randomness  and the current depth.
    print(n, n % len(fns))
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

    if isTooSmall(trig.data, angle_limit=3):
        print('Too small, aborting at n:', n)
        return [], nx.DiGraph()

    gr = nx.DiGraph()
    gr.add_node(trig)
    inlay = trig.data
    ret = []

    all_strategy_args = [trig, n] + strategy_args
    fn = strategy(*all_strategy_args)
    print(fn)
    main, extras = fn(inlay)
    main = IDNode(main)
    extras = [IDNode(extra) for extra in extras]
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
