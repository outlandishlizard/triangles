import random

import networkx as nx
import numpy as np


def mutate_color(color):
    ret = []
    for x in color:
        ret.append((x + random.randint(-4, 4)) % 255)
    return tuple(ret)


def clamp(color, low, high):
    ret = []
    for x in color:
        ret.append(low + (x % (high - low)))
    return tuple(ret)


def mutate_with_clamp(color, low=128, high=200):
    return clamp(mutate_color(color), low, high)


def cycle_color(color):
    increments = (5, 10, 15)
    ret = []
    for c, inc in zip(color, increments):
        ret.append(128 + ((c + inc) % 128))
    return tuple(ret)


def countup(gr, node):
    preds = [x for x in gr.predecessors(node)]
    if len(preds) > 1:
        print('Not a tree??')
    inherit = 0
    for pred in preds:
        inherit = max(inherit, pred.attrs['ctr'])
    node.attrs['ctr'] = inherit + 1
    return node.attrs


def inherit_color_with_mutate(gr, node, mutate_fn):
    preds = [x for x in gr.predecessors(node)]
    if len(preds) > 1:
        print('Not a tree??')
    inherit = (0, 0, 0)
    for pred in preds:
        inherit = max(inherit, pred.attrs['color'])
    node.attrs['color'] = mutate_fn(inherit)
    # print(node.attrs['color'])
    return node.attrs


def counter_to_color(ctr):
    multipliers = np.array([17, 13, 31])
    new_colors = (multipliers * ctr) % 255
    return tuple(new_colors)


def propagate_fn(gr, start, fn, fn_args, max_depth=-1):
    if max_depth == 0:
        return []
    descendants = [x for x in gr.successors(start)]
    touched_nodes = [(max_depth, start)]

    # print('descend', descendants)
    full_args = [gr, start] + fn_args
    start.attrs = fn(*full_args)
    for descendant in descendants:
        # print('desc',descendant)
        touched_nodes += propagate_fn(gr, descendant, fn, fn_args, max_depth=max_depth - 1)
    # print(gr.nodes[start])
    # print('start',start)
    return touched_nodes


def apply_inherited_color_mutate(gr):
    ordered = (list(nx.algorithms.topological_sort(gr)))
    start = ordered[0]
    start.attrs['color'] = (20, 20, 20)
    return propagate_fn(gr, start, inherit_color_with_mutate, [mutate_with_clamp])


