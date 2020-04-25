from PIL import ImageDraw
from PIL.ImagePath import *

from geolib.helpers import to_tups
from geolib.renderers.BaseRenderer import BaseRenderer


class PillowRenderer(BaseRenderer):
    def __init__(self, length=1000, width=1000, bg=(0, 0, 0), mode='RGB'):
        super().__init__()
        self.length = length
        self.width = width
        self.bg = bg
        self.mode = mode

    def draw_graph(self, gr, canvas=None, reversetop=True):
        return super().draw_graph(gr, canvas=canvas, reversetop=True)

    def draw_polygon(self, node, canvas):
        if canvas is None:
            canvas = self.blank_image()
        draw = ImageDraw.Draw(canvas)

        try:
            color = node.attrs['color']
        except KeyError:
            color = None
        try:
            fillcolor = node.attrs['fillcolor']
        except KeyError:
            fillcolor = None
        polygon = node.data
        draw.polygon(Path(to_tups(polygon)), outline=color, fill=fillcolor)
        return canvas

    @staticmethod
    def save_image(filename, img):
        return img.save(filename)

    @staticmethod
    def save_animation(filename, frame_list, format='GIF', frame_duration=50):
        return frame_list[0].save(filename, format=format, append_images=frame_list[1:], save_all=True,
                                  duration=frame_duration, loop=0)

    def copy_canvas(self, canvas):
        return canvas.copy()

    def blend_frames(self, frame1, frame2, n):
        interframes = []
        for i in range(1, n):
            alpha = i / n
            interframes.append(Image.blend(frame1, frame2, alpha))
            if interframes[-1] == frame2:
                print('stopped blend early')
                break
        return [frame1] + interframes + [frame2]

    def blank_image(self, l=None, w=None, bg=None, mode=None):
        if l is None:
            l = self.length
        if w is None:
            w = self.width
        if bg is None:
            bg = self.bg
        if mode is None:
            mode = self.mode

        return Image.new(mode, (l, w), color=bg)
