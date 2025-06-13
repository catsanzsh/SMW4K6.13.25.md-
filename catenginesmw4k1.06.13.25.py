import sys
import math
import pygame as pg
from rom_tools import SMWRomParser  # hypothetical parser

# ---------- Configuration ----------
PG_SCALE = 3
W, H, FPS = 256, 224, 60
ROM_PATH = "SuperMarioWorld.smc"

def blit_mode7(surface, tex, angle, zoom, cam):
    """Draw a Mode-7 floor onto a logical 256×224 surface."""
    half_w, half_h = W * 0.5, H * 0.5
    sin_a, cos_a = math.sin(angle), math.cos(angle)

    # Only draw on the bottom half
    for screen_y in range(int(half_h), H):
        # distance from camera plane
        dy_cam = (screen_y - half_h) / zoom
        if dy_cam <= 1e-5:
            continue
        row_scale = 1.0 / dy_cam

        # Compute world‐space start point (left edge)
        start_x = (-half_w * cos_a - half_h * sin_a) * row_scale + cam[0]
        start_y = ( half_w * sin_a - half_h * cos_a) * row_scale + cam[1]

        # How much to step in world‐space per screen pixel
        step_x = cos_a * row_scale
        step_y = sin_a * row_scale

        for screen_x in range(W):
            u = int(start_x + screen_x * step_x) % tex.get_width()
            v = int(start_y + screen_x * step_y) % tex.get_height()
            surface.set_at((screen_x, screen_y), tex.get_at((u, v)))

def render_level(surface, level_data, camera_pos, parser):
    """Blit 2D tiles and sprites on top of the floor."""
    tile_layer = level_data["tiles"]
    sprites    = level_data["sprites"]
    TILE      = 16  # SMW tiles are 16×16 px

    for r, row in enumerate(tile_layer):
        for c, tid in enumerate(row):
            if tid == 0:
                continue
            tex = parser.get_tile_surface(tid)
            x   = c * TILE - camera_pos[0]
            y   = r * TILE - camera_pos[1]
            surface.blit(tex, (x, y))

    for sp in sprites:
        tex = parser.get_sprite_surface(sp["id"])
        x   = sp["x"] - camera_pos[0]
        y   = sp["y"] - camera_pos[1]
        surface.blit(tex, (x, y))

def main():
    pg.init()
    # create a window at the *scaled* size, but render everything to logical_surface
    screen = pg.display.set_mode((W * PG_SCALE, H * PG_SCALE))
    clock  = pg.time.Clock()
    canvas = pg.Surface((W, H))

    parser    = SMWRomParser(ROM_PATH)
    WORLD_MAP, LEVELS = parser.extract_world_and_levels()

    active_world     = WORLD_MAP[0]
    active_level_id  = active_world["start_level"]
    angle            = 0.0
    camera_position  = [0.0, 0.0]

    while True:
        for ev in pg.event.get():
            if ev.type in (pg.QUIT, pg.KEYDOWN) and getattr(ev, "key", None) == pg.K_ESCAPE:
                pg.quit()
                sys.exit()

        # simple rotation demo
        angle += 0.005

        # clear canvas
        canvas.fill((0, 0, 0))

        # draw floor
        floor_tex = parser.get_floor_texture(active_world["floor_tileset"])
        blit_mode7(canvas, floor_tex, angle, zoom=120, cam=camera_position)

        # draw level overlay
        lvl_data = LEVELS[active_level_id]
        render_level(canvas, lvl_data, camera_position, parser)

        # scale up in one go
        scaled = pg.transform.scale(canvas, (W * PG_SCALE, H * PG_SCALE))
        screen.blit(scaled, (0, 0))

        pg.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
