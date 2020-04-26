import time

import cv2

from geolib.draw import apply_inherited_color_mutate, apply_fill_from_node_fast, set_zlevel
from geolib.inlays import fillingTriangle, randomTriangle, fillingTiled, doInlays, strategy_random, all_fns, \
    outlayReflect
from geolib.renderers.objrender import ObjRenderer
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
    return img


def colorprop_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])

    apply_inherited_color_mutate(gr)

    r = PillowRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    return img


def renderer_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])

    apply_inherited_color_mutate(gr)
    r = PillowRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    return img


def renderer_turtle(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns], n=1)

    apply_inherited_color_mutate(gr)
    r = TurtleRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    # img.exitonclick()
    # img.mainloop()
    return img

def colorprop_animated_pillow(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])
    # canvas = blank_image(length, width)
    canvas = None
    r = PillowRenderer(length=length, width=width, bg=(128, 128, 128))
    frames = r.animate_fn(gr, apply_inherited_color_mutate, canvas, times_to_apply=3,
                          fn_kwargs={'colorattr': 'fillcolor'}, blend=True)
    r.save_animation('./tmp.gif', frames, frame_duration=100)
    print("Pillow doesn't support .show() on GIFs, so please open tmp.gif yourself!")
    return frames


def fill_from_image(length, width, source_image=None):
    # for i in range(20):
    img = None
    if source_image is None:
        source_image = cv2.imread('../mountain.jpg')
    for i in range(1):
        for trig in fillingTiled(length, width, n=4):
            # trig -= (length,width)
            _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns], n=55)
            apply_fill_from_node_fast(gr, source_image)
            r = PillowRenderer(length=length, width=width)

            img = r.draw_graph(gr, reversetop=True, canvas=img)
    # img.mainloop()
    #img.show()
    img.save('./abstract.png')
    return img

def test_outlays(length, width):
    trig = randomTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])
    reflection, gr2 = outlayReflect(trig)
    _, gr2 = doInlays(reflection[0], strategy_random, strategy_args=[all_fns])
    gr.add_nodes_from(gr2)
    gr.add_edges_from(gr2.edges)
    apply_inherited_color_mutate(gr)
    r = PillowRenderer(length=length, width=width)
    img = r.draw_graph(gr)
    return img


def test_objrender(length, width):
    trig = fillingTriangle(length, width)
    _, gr = doInlays(trig, strategy_random, strategy_args=[all_fns])

    set_zlevel(gr)
    apply_inherited_color_mutate(gr, fn_kwargs={'colorattr': 'fillcolor'})
    r = ObjRenderer()
    img = r.draw_graph(gr)
    return img
    # r.save_image('test.obj',img)


def profileme():
    for i in range(40):
        fill_from_image(400, 600)


def tests():
    print("Attempting a basic render using pillow")
    img = basic_pillow(500, 500)
    img.save('./basic_pillow.png')
    print("Attempting a basic render with inherited color using pillow")
    img = renderer_pillow(1000, 1000)
    img.save('./renderer_pillow.png')
    print("Attempting to generate a color propagation animation using pillow")
    img = colorprop_animated_pillow(350, 350)
    PillowRenderer.save_animation('./colorprop_animated_pillow.gif', img)
    print("Attempting a render stealing colors from a source image using pillow")
    img = fill_from_image(400, 600)
    img.save('./fill_from_image.png')
    print("Testing triangle outlay features, rendering using pillow")
    img = test_outlays(2000, 2000)
    img.save('./test_outlays.png')
    print("Attempting a basic render with inherited color using turtle")
    img = renderer_turtle(1180, 450)
    # We don't save the turtle result because doing so isn't supported yet.
    print("Attempting a 3d render to .obj format using objrender backend")
    img = test_objrender(500, 500)
    img.save('./test_objrender.obj')
    pass


def main():
    tests()
    return

    # Attempt at sourcing triangle fills from live image. Probably doesn't run anymore without some work.
    # cap = cv2.VideoCapture(0)
    # cap.set(3,320)
    # cap.set(4,240)
    # while (1):
    #    ret,frame = cap.read()
    #    height,width,_ = frame.shape
    #    img = fill_from_image(height,width,frame)
    #    cv2img = np.array(img)
    #    cv2img = cv2img[:,:,::-1].copy() #bgr flip
    #    cv2.imshow('tst',cv2img)
    #    cv2.waitKey(0)


if __name__ == '__main__':
    # p = cProfile.run('main()', sort='tottime')
    prev = time.time()
    main()
    now = time.time()
    print('Completed tests in', now - prev)
