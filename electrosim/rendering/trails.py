from __future__ import annotations

from typing import Iterable, Optional, Tuple

import numpy as np
import pygame

from electrosim import config
from electrosim.simulation.engine import Particle
from electrosim.rendering.primitives import world_vector_to_screen

_TRAILS_SURF_CACHE: dict[tuple[int, int], pygame.Surface] = {}

 
def _get_trails_surface(width_px: int, height_px: int) -> pygame.Surface:
	key = (width_px, height_px)
	surf = _TRAILS_SURF_CACHE.get(key)
	if surf is None or surf.get_width() != width_px or surf.get_height() != height_px:
		surf = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
		_TRAILS_SURF_CACHE[key] = surf
	else:
		surf.fill((0, 0, 0, 0))
	return surf


def draw_trails(screen: pygame.Surface, particles: Iterable[Particle], pixels_per_meter: float) -> None:
	"""Render faded line segments approximating recent particle trajectories."""
	width_px = config.WINDOW_WIDTH_PX
	height_px = config.WINDOW_HEIGHT_PX
	max_dx = width_px // 2
	max_dy = height_px // 2

	trails_surface = _get_trails_surface(width_px, height_px)

	for p in particles:
		if not p.history:
			continue
		if abs(p.charge_c) <= config.NEUTRAL_CHARGE_EPS:
			base_rgb = config.COLOR_NEUTRAL
		else:
			base_rgb = config.COLOR_TRAIL_POS if p.charge_c > 0 else config.COLOR_TRAIL_NEG

		t_now = p.history[-1][0]

		prev_pt: Optional[Tuple[int, int]] = None
		prev_t: Optional[float] = None
		for (t, xy) in p.history:
			pt = world_vector_to_screen(np.array([xy[0], xy[1]]), pixels_per_meter)
			if prev_pt is not None and prev_t is not None:
				dx = abs(pt[0] - prev_pt[0])
				dy = abs(pt[1] - prev_pt[1])
				if dx > max_dx or dy > max_dy:
					prev_pt = pt
					prev_t = t
					continue

				age = max(0.0, float(t_now - t))
				if config.TRAIL_FADE_SECONDS > 1e-9:
					w = max(0.0, min(1.0, 1.0 - age / float(config.TRAIL_FADE_SECONDS)))
				else:
					w = 1.0
				alpha_core = int(round(config.TRAIL_ALPHA_MAX * w))
				if alpha_core >= config.TRAIL_MIN_ALPHA:
					alpha_edge = int(round(alpha_core * config.TRAIL_AA_EDGE_OPACITY_FACTOR))
					if alpha_edge > 0:
						color_edge = (base_rgb[0], base_rgb[1], base_rgb[2], alpha_edge)
						pygame.draw.line(
							trails_surface,
							color_edge,
							prev_pt,
							pt,
							config.TRAIL_WIDTH_PX + 2 * config.TRAIL_AA_EDGE_EXTEND_PX,
						)
					color_core = (base_rgb[0], base_rgb[1], base_rgb[2], alpha_core)
					pygame.draw.line(
						trails_surface,
						color_core,
						prev_pt,
						pt,
						config.TRAIL_WIDTH_PX,
					)

			prev_pt = pt
			prev_t = t

	screen.blit(trails_surface, (0, 0))


def draw_polyline_world(
	screen: pygame.Surface,
	points_world: Iterable[tuple[float, float]],
	color_rgb: tuple[int, int, int],
	width_px: int,
	pixels_per_meter: float,
) -> None:
	"""Draw a simple polyline through a sequence of world positions.

	Parameters
	----------
	screen : pygame.Surface
		Target surface.
	points_world : Iterable[tuple[float, float]]
		Sequence of (x, y) in meters.
	color_rgb : tuple[int,int,int]
		Polyline color.
	width_px : int
		Line width in pixels.
	pixels_per_meter : float
		Pixels-per-meter scale.
	"""
	pts_screen: list[tuple[int, int]] = []
	for (x, y) in points_world:
		pts_screen.append(world_vector_to_screen(np.array([float(x), float(y)]), pixels_per_meter))
	if len(pts_screen) >= 2:
		pygame.draw.lines(screen, color_rgb, False, pts_screen, max(1, int(width_px)))


