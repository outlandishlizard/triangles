import random

import networkx as nx
import numpy as np

import geolib.imageprocessing
import geolib.iterators


def get_leaves(gr):
    return [x[0] for x in gr.out_degree() if x[1] == 0]


def get_roots(gr):
    return [x[0] for x in gr.in_degree() if x[1] == 0]

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
        inherit = max(inherit, pred.attrs['zlevel'])
    node.attrs['zlevel'] = inherit + 1
    return node.attrs


def inherit_both(gr, node, mutate_fn, colorattr='color'):
    inherit_color_with_mutate(gr, node, mutate_fn, colorattr='fillcolor')
    inherit_color_with_mutate(gr, node, mutate_fn, colorattr='color')
    # node.attrs['color'] = tuple([max(0,x-20) for x in node.attrs['fillcolor']])
    return node.attrs


def inherit_color_with_mutate(gr, node, mutate_fn, colorattr='color'):
    # print(colorattr)
    preds = [x for x in gr.predecessors(node)]
    if len(preds) > 1:
        print('Not a tree??')
    inherit = (0, 0, 0)
    for pred in preds:
        try:
            inherit = max(inherit, pred.attrs[colorattr])
        except KeyError:
            inherit = max(inherit, (20, 20, 20))
    node.attrs[colorattr] = mutate_fn(inherit)
    # print(node.attrs['color'])
    return node.attrs


def counter_to_color(ctr):
    multipliers = np.array([17, 13, 31])
    new_colors = (multipliers * ctr) % 255
    return tuple(new_colors)


def propagate_fn(gr, start, fn, fn_args, fn_kwargs=None, max_depth=-1):
    if max_depth == 0:
        return []
    if fn_kwargs is None:
        fn_kwargs = {}
    # print(fn_kwargs)
    descendants = [x for x in gr.successors(start)]

    touched_nodes = [(max_depth, start)]

    full_args = [gr, start] + fn_args
    start.attrs = fn(*full_args, **fn_kwargs)
    for descendant in descendants:
        touched_nodes += propagate_fn(gr, descendant, fn, fn_args, fn_kwargs, max_depth=max_depth - 1)
    return touched_nodes


# unlike propagate_fn, this hits the whole graph, not just everything below the root node.
def map_onto_graph(gr, fn, fn_args, fn_kwargs=None):
    if fn_kwargs is None:
        fn_kwargs = {}
    nodes = reversed(list(nx.algorithms.topological_sort(gr)))
    return [fn(*([node] + fn_args), **fn_kwargs) for node in nodes]


def color_from_node(node, image):
    return geolib.imageprocessing.color_from_path(node, image)


def fill_from_node(node, image):
    node.attrs['fillcolor'] = color_from_node(node, image)


def apply_fill_from_node(gr, image):
    map_onto_graph(gr, fill_from_node, [image])


def propagate_from_leaves(gr, fn, fn_args, fn_kwargs=None):
    if fn_kwargs is None:
        fn_kwargs = {}
    next_nodes = []
    for leaf in get_leaves(gr):
        next_nodes += gr.predecessors(leaf)
        args = [leaf] + fn_args
        fn(*args, **fn_kwargs)
    while next_nodes:
        after = []
        for node in next_nodes:
            after += gr.predecessors(node)
            args = [node] + fn_args
            fn(*args, **fn_kwargs)
        next_nodes = after
    return


def propagate_toward_root(gr, fn, fn_args, fn_kwargs=None):
    if fn_kwargs is None:
        fn_kwargs = {}
    ordered = (list(nx.algorithms.topological_sort(gr)))
    start = ordered[0]
    paths = nx.single_source_shortest_path_length(gr, start)
    for node, dist in reversed(sorted(paths.items(), key=lambda x: x[1])):
        args = [node] + fn_args
        fn(*args, **fn_kwargs)


def iteratorstyle_from_root(gr, fn, fn_args, fn_kwargs=None):
    rets = []
    if fn_kwargs is None:
        fn_kwargs = {}
    layers = geolib.iterators.walk_down_from_roots(gr)
    # The iterator style walks return an ordered list of lists of nodes, whereas animation expects a list of tuples of
    # (depth, node), so we do some translation here.

    for ctr, layer in enumerate(layers):
        for node in layer:
            args = [gr, node] + fn_args
            depth = len(layers) - ctr
            fn(*args, **fn_kwargs)
            rets.append((depth, node))
    # print('expected node touches:', len(rets))
    return rets


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


def _apply_inherited_color_mutate(gr, fn_kwargs=None):
    if fn_kwargs is None:
        fn_kwargs = {}
    # ordered = (list(nx.algorithms.topological_sort(gr)))
    # start = ordered[0]
    rets = []
    for start in get_roots(gr):
        try:
            colorattr = fn_kwargs['colorattr']
        except KeyError:
            colorattr = 'color'
        if not colorattr in start.attrs:
            start.attrs[colorattr] = (20, 20, 20)
        # We build up a list here from the results of calling from each root-- this might get messy later if we want
        # to handle those individually for some reason in animation
        rets += iteratorstyle_from_root(gr, inherit_color_with_mutate, [mutate_with_clamp],
                                        fn_kwargs={'colorattr': colorattr})
        # rets += propagate_fn(gr, start, inherit_both, [mutate_with_clamp], fn_kwargs={'colorattr':colorattr})
    return rets


def apply_inherited_color_mutate(gr, fn_kwargs=None):
    if fn_kwargs is None:
        fn_kwargs = {}
    # ordered = (list(nx.algorithms.topological_sort(gr)))
    # start = ordered[0]
    rets = []
    try:
        colorattr = fn_kwargs['colorattr']
    except KeyError:
        colorattr = 'color'
    for root in get_roots(gr):
        root.attrs[colorattr] = (20, 20, 20)

    rets += iteratorstyle_from_root(gr, inherit_both, [mutate_with_clamp], fn_kwargs={'colorattr': colorattr})
    # rets += propagate_fn(gr, start, inherit_both, [mutate_with_clamp], fn_kwargs={'colorattr':colorattr})
    return rets


def set_zlevel(gr):
    ordered = (list(nx.algorithms.topological_sort(gr)))
    start = ordered[0]
    propagate_fn(gr, start, countup, [])
