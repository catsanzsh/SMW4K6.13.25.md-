"""
test.py – minimal SMW‑style engine (60 FPS, Mode‑7 floor)
Run:  python test.py
Deps: pygame>=2.5.0, numpy, scipy   (for SPC‑like DSP later)
"""

import sys, pygame as pg, numpy as np, math
from output import WORLD_MAP, LEVELS   # your data stubs

pg.init()
W, H, FPS = 256, 224, 60
screen = pg.display.set_mode((W * 3, H * 3), pg.SCALED)
clock = pg.time.Clock()

# ---------- Mode‑7 style floor (affine texture on each scanline) ----------
def blit_mode7(surface, tex, angle, zoom):
    cx, cy = tex.get_width() // 2, tex.get_height() // 2
    sin, cos = math.sin(angle), math.cos(angle)
    for y in range(H):
        dy = (y - H / 2) / zoom
        if dy == 0: continue
        sx_step = cos / dy
        sy_step = sin / dy
        sx = cx + (-W / 2) * sx_step
        sy = cy + (-W / 2) * sy_step
        line = pg.Surface((W, 1), pg.SRCALPHA)
        for x in range(W):
            line.set_at((x, 0), tex.get_at((int(sx) % tex.get_width(),
                                            int(sy) % tex.get_height())))
            sx += sx_step; sy += sy_step
        surface.blit(pg.transform.scale(line, (W * 3, 3)), (0, y * 3))

# ---------- Main loop ----------
tex = pg.Surface((512, 512)); tex.fill("darkslateblue")  # placeholder “vibes”
angle = 0.0
while True:
    for ev in pg.event.get():
        if ev.type == pg.QUIT or (ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE):
            pg.quit(); sys.exit()
    angle += 0.005
    blit_mode7(screen, tex, angle, zoom=120)

    # TODO: update player, sprites, camera, etc. using LEVELS[active_id]
    pg.display.flip()
    clock.tick(FPS)
