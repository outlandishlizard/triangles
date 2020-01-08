from src.draw import draw_graph
from src.inlays import randomTriangle, doInlays, strategy_samerandom, all_fns

LEN = 1000
WID = 1000
trig = randomTriangle(LEN, WID)
_, gr = doInlays(trig, strategy_samerandom, strategy_args=[all_fns, 1234])
img = draw_graph(gr, length=LEN, width=WID)
img.show()
