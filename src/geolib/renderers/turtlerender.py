from turtle import Screen, RawTurtle

from geolib.helpers import to_tups
from geolib.renderers.BaseRenderer import BaseRenderer


class TurtleRenderer(BaseRenderer):

    def __init__(self, length=1000, width=1000, bg=(0, 0, 0), mode=255):
        super().__init__()
        self.length = length
        self.width = width
        self.bg = bg
        self.mode = mode

    def translate_coords(self, screen, point):
        print('translate:', point)
        print(screen.screensize())
        x = point[0] - screen.screensize()[0] / 2
        y = point[1] - screen.screensize()[1] / 2
        return x, -y

    def draw_polygon(self, polygon, screen, linecolor=None, fillcolor=None):
        pen = RawTurtle(screen)
        pen.speed(0)
        pen.hideturtle()
        pen.penup()

        if linecolor is not None:
            pen.pencolor(*linecolor)
        else:
            pen.pencolor(*(0, 0, 0))

        polygon = [self.translate_coords(screen, x) for x in polygon]
        points = to_tups(polygon)
        pen.goto(*(points[0]))
        pen.pendown()
        if fillcolor:
            pen.fillcolor(*fillcolor)
            pen.pencolor(*fillcolor)
            pen.begin_fill()
        for point in points[::-1]:
            pen.goto(*point)
        if fillcolor:
            pen.end_fill()

    def copy_canvas(self, screen):
        raise NotImplementedError

    def blank_image(self, l=None, w=None, bg=None, mode=None):
        if l is None:
            l = self.length
        if w is None:
            w = self.width
        if bg is None:
            bg = self.bg
        if mode is None:
            mode = self.mode
        screen = Screen()
        screen.setup(width=l, height=w, startx=0, starty=0)
        screen.screensize(l, w)
        screen.bgcolor(*bg)
        screen.colormode(mode)
        screen.delay(0)
        return screen
