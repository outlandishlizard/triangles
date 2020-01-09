
import networkx as nx
from PIL import ImageDraw
from PIL.ImagePath import *

from .helpers import to_tups


def draw_graph(gr, canvas):
    canvas = canvas.copy()
    draw = ImageDraw.Draw(canvas)

    topological_ordered = list(reversed(list(nx.algorithms.topological_sort(gr))))
    for node in topological_ordered:
        data = node.data
        try:
            color = node.attrs['color']
        except KeyError:
            color = (255, 0, 0)
        draw.polygon(Path(to_tups(data)), outline=color)
    return canvas


def draw_nodes(nodes, canvas):
    canvas = canvas.copy()
    draw = ImageDraw.Draw(canvas)

    for node in nodes:
        data = node.data
        color = node.attrs['color']
        draw.polygon(Path(to_tups(data)), outline=color)
    return canvas


def blend_frames(frame1, frame2, n):
    interframes = []
    for i in range(1, n):
        alpha = i / n
        interframes.append(Image.blend(frame1, frame2, alpha))
        if interframes[-1] == frame2:
            print('stopped blend early')
            break
    return [frame1] + interframes + [frame2]

def animate_fn(gr, fn, canvas, times_to_apply=25):
    frame_list = []
    frame = canvas.copy()
    for i in range(times_to_apply):
        changelist = sorted(fn(gr))[::-1]
        curr = changelist[0][0]
        nodes = []
        for generation, node in changelist:
            if generation != curr:
                prev_frame = frame
                frame = draw_nodes(nodes, frame)
                frame_list += blend_frames(prev_frame, frame, 5)
                frame_list.append(frame)
                nodes = []
            nodes.append(node)
            curr = generation
    return frame_list


def save_animation(filename, frame_list, format='GIF', frame_duration=50):
    return frame_list[0].save(filename, format=format, append_images=frame_list[1:], save_all=True,
                              duration=frame_duration, loop=0, optimize=True)


def blank_image(l, w, bg=(0, 0, 0), mode='RGB'):
    return Image.new(mode, (l, w), color=bg)
