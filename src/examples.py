
from geolib.draw import apply_inherited_color_mutate
from geolib.inlays import fillingTriangle, doInlays, strategy_random, all_fns
from geolib.pillow import animate_fn, save_animation, blank_image
from geolib.turtlerender import draw_graph as draw_graph_turtle

def basic_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])
    canvas = blank_image(length, width)
    img = draw_graph_turtle(gr, canvas)
    img.show()


def colorprop_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])

    apply_inherited_color_mutate(gr)

    canvas = blank_image(length, width)
    img = draw_graph_turtle(gr, canvas)
    img.show()


def colorprop_animated_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])
    canvas = blank_image(length, width)

    frames = animate_fn(gr, apply_inherited_color_mutate, canvas, times_to_apply=3)
    save_animation('./tmp.gif', frames)
    print("Pillow doesn't support .show() on GIFs, so please open tmp.gif yourself!")
if __name__ == '__main__':
    # colorprop_animated_pillow(350, 350)
    # basic_pillow(500, 500)
    colorprop_pillow(500, 500)
