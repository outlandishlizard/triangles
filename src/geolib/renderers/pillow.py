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

    def draw_polygon(self, polygon, canvas, linecolor=None, fillcolor=None):
        draw = ImageDraw.Draw(canvas)
        draw.polygon(Path(to_tups(polygon)), outline=linecolor, fill=fillcolor)

    def save_image(self, filename, img):
        return img.save(filename)

    def save_animation(self, filename, frame_list, format='GIF', frame_duration=50):
        return frame_list[0].save(filename, format=format, append_images=frame_list[1:], save_all=True,
                                  duration=frame_duration, loop=0, optimize=True)

    def copy_canvas(self, canvas):
        return canvas.copy()

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
