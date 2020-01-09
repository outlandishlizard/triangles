from turtle import Turtle, Screen

import networkx as nx

from .helpers import to_tups


def draw_graph(gr, screen):
    screen = Screen()
    screen.bgcolor("black")
    screen.delay(0)
    screen.colormode(255)
    topological_ordered = list(reversed(list(nx.algorithms.topological_sort(gr))))
    for node in topological_ordered:
        data = node.data
        try:
            color = node.attrs['color']
        except KeyError:
            color = (255, 0, 0)
        pen = Turtle()
        pen.hideturtle()
        pen.penup()
        pen.pencolor(*color)
        points = to_tups(data)
        pen.goto(*(points[0]))
        pen.pendown()
        for point in points[::-1]:
            pen.goto(*point)
            # print(color,point)
    screen.mainloop()
