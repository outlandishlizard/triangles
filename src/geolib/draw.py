import random

import networkx as nx
import numpy as np

import geolib.imageprocessing


def get_leaves(gr):
    return [x[0] for x in gr.out_degree() if x[1] == 0]


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

    full_args = [gr, start] + fn_args
    start.attrs = fn(*full_args)
    for descendant in descendants:
        touched_nodes += propagate_fn(gr, descendant, fn, fn_args, max_depth=max_depth - 1)
    return touched_nodes


# unlike propagate_fn, this hits the whole graph, not just everything below the root node.
def map_onto_graph(gr, fn, fn_args):
    nodes = reversed(list(nx.algorithms.topological_sort(gr)))
    return [fn(*([node] + fn_args)) for node in nodes]


def color_from_node(node, image):
    return geolib.imageprocessing.color_from_path([np.int32(node.data)], image)


def fill_from_node(node, image):
    node.attrs['fillcolor'] = color_from_node(node, image)


def apply_fill_from_node(gr, image):
    map_onto_graph(gr, fill_from_node, [image])


def propagate_from_leaves(gr, fn, fn_args):
    next_nodes = []
    for leaf in get_leaves(gr):
        next_nodes += gr.predecessors(leaf)
        args = [leaf] + fn_args
        fn(*args)
    while next_nodes:
        after = []
        for node in next_nodes:
            after += gr.predecessors(node)
            args = [node] + fn_args
            fn(*args)
        next_nodes = after
    return


def propagate_toward_root(gr, fn, fn_args):
    ordered = (list(nx.algorithms.topological_sort(gr)))
    start = ordered[0]
    paths = nx.single_source_shortest_path_length(gr, start)
    for node, dist in reversed(sorted(paths.items(), key=lambda x: x[1])):
        args = [node] + fn_args
        fn(*args)


def fill_from_node_fast(node, gr, image):
    all_children = [x for x in gr.successors(node)]
    child_fillings = [x.attrs['fillcolor'] for x in all_children if 'fillcolor' in x.attrs]

    if child_fillings and (len(all_children) == len(child_fillings)):
        ra = int(sum(x[0] for x in child_fillings) / len(child_fillings))
        ba = int(sum(x[1] for x in child_fillings) / len(child_fillings))
        ga = int(sum(x[2] for x in child_fillings) / len(child_fillings))

        node.attrs['fillcolor'] = (ra, ba, ga)
        return

    node.attrs['fillcolor'] = color_from_node(node, image)


def apply_fill_from_node_fast(gr, image):
    propagate_toward_root(gr, fill_from_node_fast, [gr, image])


def apply_inherited_color_mutate(gr):
    ordered = (list(nx.algorithms.topological_sort(gr)))
    start = ordered[0]
    start.attrs['color'] = (20, 20, 20)
    return propagate_fn(gr, start, inherit_color_with_mutate, [mutate_with_clamp])
