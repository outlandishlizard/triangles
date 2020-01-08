from geolib.draw import apply_inherited_color_mutate
from geolib.inlays import randomTriangle, doInlays, strategy_random, all_fns
from geolib.pillow import draw_graph, blank_image


def basic_pillow(length, width):
    trig = randomTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])
    canvas = blank_image(length, width)
    img = draw_graph(gr, canvas)
    img.show()


def colorprop_pillow(length, width):
    trig = randomTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])

    apply_inherited_color_mutate(gr)

    canvas = blank_image(length, width)
    img = draw_graph(gr, canvas)
    img.show()


if __name__ == '__main__':
    basic_pillow(5000, 5000)
    colorprop_pillow(5000, 5000)
