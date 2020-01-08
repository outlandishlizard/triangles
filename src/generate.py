from geolib.inlays import randomTriangle, doInlays, strategy_samerandom, all_fns
from geolib.pillow import draw_graph, blank_image

LEN = 1000
WID = 1000
trig = randomTriangle(LEN, WID)
_, gr = doInlays(trig, strategy_samerandom, strategy_args=[all_fns, 1234])
canvas = blank_image(LEN, WID)
img = draw_graph(gr, canvas)
img.show()
