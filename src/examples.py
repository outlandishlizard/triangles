import cProfile

import cv2

from geolib.draw import apply_inherited_color_mutate, apply_fill_from_node_fast
from geolib.inlays import fillingTriangle, randomTriangle, fillingTiled, doInlays, strategy_random, all_fns, \
    outlayReflect
from geolib.pillow import animate_fn, save_animation, blank_image
from geolib.renderers.pillow import PillowRenderer
from geolib.renderers.turtlerender import TurtleRenderer


def testable(function):
    def wrapper(*args, **kwargs):
        pass


def basic_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])
    r = PillowRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    img.show()


def colorprop_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])

    apply_inherited_color_mutate(gr)

    r = PillowRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    img.show()


def renderer_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])

    apply_inherited_color_mutate(gr)
    r = PillowRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    img.show()


def renderer_turtle(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns], n=1)

    apply_inherited_color_mutate(gr)
    r = TurtleRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    img.mainloop()


def colorprop_animated_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])
    canvas = blank_image(length, width)

    frames = animate_fn(gr, apply_inherited_color_mutate, canvas, times_to_apply=3)
    save_animation('./tmp.gif', frames)
    print("Pillow doesn't support .show() on GIFs, so please open tmp.gif yourself!")


def fill_from_image(length, width):
    # for i in range(20):
    img = None
    mountain = cv2.imread('../mushrooms.jpg')
    for i in range(1):
        for trig in fillingTiled(length, width, n=10):
            # trig -= (length,width)
            _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns], n=55)
            apply_fill_from_node_fast(gr, mountain)
            r = PillowRenderer(length=length, width=width)

            img = r.draw_graph(gr, reversetop=True, canvas=img)
    # img.mainloop()
    # img.show()
    img.save('./abstract.png')


def test_outlays(length, width):
    trig = randomTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])
    reflection, gr2 = outlayReflect(trig)
    gr.add_nodes_from(gr2)
    apply_inherited_color_mutate(gr)
    r = PillowRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    img.show()


def main():
    colorprop_animated_pillow(350, 350)
    basic_pillow(500, 500)
    renderer_pillow(500, 500)
    fill_from_image(400, 600)
    test_outlays(2000, 2000)
    # renderer_turtle(1180,450)
    pass


if __name__ == '__main__':
    p = cProfile.run('main()', sort='tottime')
