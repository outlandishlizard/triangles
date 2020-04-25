import networkx as nx


class BaseRenderer(object):
    def __init__(self):
        pass

    def draw_graph(self, gr, canvas=None, reversetop=False):
        if canvas is None:
            canvas = self.blank_image()

        topological_ordered = list(reversed(list(nx.algorithms.topological_sort(gr))))
        if reversetop:
            topological_ordered = reversed(topological_ordered)
        for node in topological_ordered:
            self.draw_polygon(node, canvas)
        return canvas

    def draw_nodes(self, nodes, canvas=None):
        if canvas is None:
            canvas = self.blank_image()

        for node in nodes:
            canvas = self.draw_polygon(node, canvas)
        return canvas

    def animate_fn(self, gr, fn, canvas, fn_kwargs=None, times_to_apply=25, bounce=True, blend=False):
        if canvas is None:
            canvas = self.blank_image()
        if fn_kwargs is None:
            fn_kwargs = {}
        frame_list = []
        frame = canvas
        flip_it = -1
        for i in range(times_to_apply):
            changelist = sorted(fn(gr, fn_kwargs=fn_kwargs))[::flip_it]
            if bounce:
                flip_it *= -1
            curr = changelist[0][0]
            nodes = []
            for generation, node in changelist:
                if generation != curr:
                    prev_frame = frame
                    frame = self.draw_nodes(nodes, frame.copy())
                    if not blend:
                        frame_list.append(frame)
                    else:
                        frame_list += self.blend_frames(prev_frame, frame, 5)

                    nodes = []
                nodes.append(node)
                curr = generation
        print(frame_list)
        return frame_list

    def draw_polygon(self, polygon, canvas, linecolor=None, fillcolor=None):
        raise NotImplementedError

    def save_animation(self, filename, frame_list, format='GIF', frame_duration=50):
        raise NotImplementedError

    def save_image(self, filename, img):
        raise NotImplementedError

    def blank_image(self, l=None, w=None, bg=None):
        raise NotImplementedError

    def copy_canvas(self, canvas):
        raise NotImplementedError
