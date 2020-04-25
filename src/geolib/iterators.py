def get_leaves(gr):
    return [x[0] for x in gr.out_degree() if x[1] == 0]


def get_roots(gr):
    return [x[0] for x in gr.in_degree() if x[1] == 0]


# This finds all leaves of all trees in the graph, and returns a list of layers of nodes, where the leaves are the first
# layer, the parents of the leaves are the second layer, and so on, up to the roots. If the trees vary in depth, this
# means shallower trees will finish before deeper trees. This may touch nodes more than once if the node in question
# has multiple leaves as its transitive children at different depths.
def walk_up_from_leaves(gr):
    leaves = get_leaves(gr)
    layers = []

    nextlayer = []
    for leaf in leaves:
        nextlayer += gr.predecessors(leaf)
    while nextlayer != []:
        new_nextlayer = []
        for node in nextlayer:
            new_nextlayer += gr.predecessors(node)
        nextlayer = list(set(nextlayer))
        layers.append(nextlayer)
        nextlayer = new_nextlayer
    return layers


# This is implemented the same way as walk_up_from_leaves, except we start with the roots and find their successors,
# note that this will NOT return the same thing as reversed(walk_up_from_leaves) in most cases, as in any case where
# not all leaves are at the same depth, the shallower leaves will be handled differently (they'll be in the last layer
# of reversed(walk_up_from_leaves) but the nth layer of walk_down_from_roots, where n is their depth).
def walk_down_from_roots(gr):
    roots = get_roots(gr)
    layers = []

    nextlayer = []
    for root in roots:
        nextlayer += gr.successors(root)
    while nextlayer != []:
        new_nextlayer = []
        for node in nextlayer:
            new_nextlayer += gr.successors(node)
        nextlayer = list(set(nextlayer))
        layers.append(nextlayer)
        nextlayer = new_nextlayer
    return layers


# This is an alternative walk upward from the leaves that attempts to give a more useful result in trees with widely
# varying leaf depth-- rather than processing a parent node in the next layer when ANY leaf has it as a parent, here we
# wait to process a parent until ALL of its transitive children have been processed.
def walk_up_from_leaves_with_join(gr):
    leaves = get_leaves(gr)
    layers = []
    already_processed = {}
    nodes = leaves
    layers.append(leaves)
    while nodes != []:
        potential_next = []
        confirmed_next = []

        for node in nodes:
            already_processed[node] = True
            potential_next += gr.predecessors(node)
        for potential in potential_next:
            below = gr.successors(potential)
            is_already_seen = [x in already_processed for x in below]
            if all(is_already_seen):
                confirmed_next.append(potential)
        layers.append(confirmed_next)
        nodes = confirmed_next
