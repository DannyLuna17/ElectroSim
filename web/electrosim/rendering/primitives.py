from __future__ import annotations

from typing import Tuple

import numpy as np
import pygame

from electrosim import config
_GLOW_CACHE = {}

 
def world_vector_to_screen(pos_meters: np.ndarray, pixels_per_meter: float) -> Tuple[int, int]:
	"""Convert world coordinates (m) to integer screen pixels.

	Parameters
	----------
	pos_meters : numpy.ndarray shape (2,)
		World position in meters.
	pixels_per_meter : float
		Pixels per meter scale.

	Returns
	-------
	tuple[int, int]
		Pixel coordinates.
	"""
	x = int(round(pos_meters[0] * pixels_per_meter))
	y = int(round(pos_meters[1] * pixels_per_meter))
	return x, y


def screen_vector_to_world(pos_pixels: Tuple[int, int], pixels_per_meter: float) -> np.ndarray:
	"""Convert integer screen pixels to world meters as a float array.

	Parameters
	----------
	pos_pixels : tuple[int, int]
		Pixel coordinates.
	pixels_per_meter : float
		Pixels per meter scale.

	Returns
	-------
	numpy.ndarray shape (2,)
		World position in meters.
	"""
	return np.array([pos_pixels[0] / pixels_per_meter, pos_pixels[1] / pixels_per_meter], dtype=float)


def _draw_arrow(surface: pygame.Surface, color: Tuple[int, int, int] | Tuple[int, int, int, int], start_pixel: Tuple[int, int], vec_pixel: Tuple[float, float], max_len_pixel: float) -> None:
	"""Draw a clamped arrow vector from a starting pixel with a small head.

	Clamps the vector to `max_len_pixel`, draws a line, then a triangular head.
	"""
	x0, y0 = start_pixel
	vx, vy = vec_pixel
	length = float((vx * vx + vy * vy) ** 0.5)
	if length <= 1e-6:
		return
	factor = min(1.0, max_len_pixel / length)
	vx *= factor
	vy *= factor
	end = (int(x0 + vx), int(y0 + vy))
	pygame.draw.line(surface, color, (x0, y0), end, 2)

	# Arrow head
	import math as _math
	angle = _math.atan2(vy, vx)
	head_len = 8
	head_ang = _math.radians(25)
	p1 = (int(end[0] - head_len * _math.cos(angle - head_ang)), int(end[1] - head_len * _math.sin(angle - head_ang)))
	p2 = (int(end[0] - head_len * _math.cos(angle + head_ang)), int(end[1] - head_len * _math.sin(angle + head_ang)))
	pygame.draw.polygon(surface, color, [end, p1, p2])


def draw_meter_grid(screen: pygame.Surface, world_size_m: np.ndarray, pixels_per_meter: float) -> None:
	"""Draw a metric grid in meters over the entire world size.

	Major lines and colors are controlled via `config` constants.
	"""
	step_m = config.GRID_METER_STEP
	major_every = config.GRID_MAJOR_EVERY
	width_px = int(round(world_size_m[0] * pixels_per_meter))
	height_px = int(round(world_size_m[1] * pixels_per_meter))
	# Vertical lines
	x_m = 0.0
	idx = 0
	while x_m <= world_size_m[0] + 1e-9:
		x_px = int(round(x_m * pixels_per_meter))
		is_major = (idx % major_every == 0)
		color = config.COLOR_GRID_MAJOR if is_major else config.COLOR_GRID
		thickness = config.GRID_MAJOR_LINE_WIDTH if is_major else config.GRID_LINE_WIDTH
		pygame.draw.line(screen, color, (x_px, 0), (x_px, height_px), thickness)
		x_m += step_m
		idx += 1
	# Horizontal lines
	y_m = 0.0
	idx = 0
	while y_m <= world_size_m[1] + 1e-9:
		y_px = int(round(y_m * pixels_per_meter))
		is_major = (idx % major_every == 0)
		color = config.COLOR_GRID_MAJOR if is_major else config.COLOR_GRID
		thickness = config.GRID_MAJOR_LINE_WIDTH if is_major else config.GRID_LINE_WIDTH
		pygame.draw.line(screen, color, (0, y_px), (width_px, y_px), thickness)
		y_m += step_m
		idx += 1


def draw_glow_at_screen_pos(
	screen: pygame.Surface,
	center_px: Tuple[int, int],
	base_radius_px: int,
	color_rgb: Tuple[int, int, int],
	intensity: float,
) -> None:
	"""Draw a blurred radial glow using concentric alpha circles.

	Parameters
	----------
	screen : pygame.Surface
		Target surface.
	center_px : tuple[int, int]
		Center pixel.
	base_radius_px : int
		Base radius for the core circle.
	color_rgb : tuple[int,int,int]
		Glow color.
	intensity : float
		[0,1] normalized intensity, typically |q|/MAX_CHARGE_C.
	"""
	if not config.GLOW_ENABLED:
		return
	if intensity <= 0.0:
		return

	outer_radius_px = max(base_radius_px, int(round(base_radius_px * (1.0 + intensity * config.GLOW_RADIUS_SCALE))))
	size = (outer_radius_px * 2 + 2, outer_radius_px * 2 + 2)
	q_steps = max(1, int(getattr(config, "GLOW_CACHE_INTENSITY_STEPS", 32)))
	q_int = int(round(min(max(intensity, 0.0), 1.0) * q_steps))
	key = (size[0], size[1], color_rgb[0], color_rgb[1], color_rgb[2], q_int, base_radius_px)
	glow_surface = _GLOW_CACHE.get(key)
	if glow_surface is None:
		glow_surface = pygame.Surface(size, pygame.SRCALPHA)

		alpha_center = max(0, min(255, int(round((q_int / float(q_steps)) * config.GLOW_ALPHA_AT_MAX))))
		glow_surface.fill((0, 0, 0, 0))
		w = size[0]
		h = size[1]
		cx = outer_radius_px + 1
		cy = outer_radius_px + 1
		x = np.arange(w, dtype=float) - float(cx)
		y = np.arange(h, dtype=float) - float(cy)
		xx, yy = np.meshgrid(x, y, indexing="xy")
		r = np.hypot(xx, yy)
		rnorm = r / float(outer_radius_px)
		falloff = np.clip(1.0 - rnorm, 0.0, 1.0) ** 3
		rgb_view = pygame.surfarray.pixels3d(glow_surface)
		falloff_T = falloff.T
		rgb_view[:, :, 0] = (color_rgb[0] * falloff_T).astype(np.uint8)
		rgb_view[:, :, 1] = (color_rgb[1] * falloff_T).astype(np.uint8)
		rgb_view[:, :, 2] = (color_rgb[2] * falloff_T).astype(np.uint8)
		del rgb_view
		alpha = (alpha_center * falloff).astype(np.uint8)
		alpha_view = pygame.surfarray.pixels_alpha(glow_surface)
		alpha_view[:, :] = alpha.T
		del alpha_view
		# bound cache
		max_cache = int(getattr(config, "GLOW_CACHE_MAX_SURFACES", 128))
		if len(_GLOW_CACHE) >= max_cache:
			_GLOW_CACHE.pop(next(iter(_GLOW_CACHE)))
		_GLOW_CACHE[key] = glow_surface

	screen.blit(glow_surface, (center_px[0] - outer_radius_px - 1, center_px[1] - outer_radius_px - 1), special_flags=pygame.BLEND_ADD)


