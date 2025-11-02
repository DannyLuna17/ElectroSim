from __future__ import annotations

from typing import Iterable

import numpy as np
import pygame

from electrosim import config
from electrosim.simulation.engine import Particle
from electrosim.simulation.physics import electric_field_at_point
from electrosim.rendering.field_sampler import ElectricFieldSampler
from electrosim.rendering.primitives import _draw_arrow
 

_SAMPLER_CACHE: dict[tuple[int, int, int, int, int], ElectricFieldSampler] = {}


def _get_sampler(world_size_m: np.ndarray, ppm: float, grid_step_px: int, softening_fraction: float) -> ElectricFieldSampler:
	"""Return a cached `ElectricFieldSampler` for the given parameters.

	Parameters
	----------
	world_size_m : numpy.ndarray shape (2,)
		World size (m) as (Lx, Ly).
	ppm : float
		Pixels per meter.
	grid_step_px : int
		Grid spacing in pixels between field sample points.
	softening_fraction : float
		Softening fraction used for field evaluation.

	Returns
	-------
	ElectricFieldSampler
		Sampler instance cached per `(world_size, ppm, grid_step_px, softening_fraction)`.
	"""
	key = (
		int(round(world_size_m[0] * 1e6)),
		int(round(world_size_m[1] * 1e6)),
		int(round(ppm * 1000)),
		int(grid_step_px),
		int(round(softening_fraction * 1e6)),
	)
	sampler = _SAMPLER_CACHE.get(key)
	if sampler is None:
		sampler = ElectricFieldSampler(world_size_m=world_size_m, pixels_per_meter=ppm, grid_step_px=grid_step_px, softening_fraction=softening_fraction)
		_SAMPLER_CACHE[key] = sampler
	return sampler


def draw_field_grid(screen: pygame.Surface, particles: Iterable[Particle], world_size_m: np.ndarray, pixels_per_meter: float, grid_step_px: int, softening_fraction: float) -> None:
	"""Draw electric field arrows on a pixel grid using selected visualization mode."""
	width_px = int(round(world_size_m[0] * pixels_per_meter))
	height_px = int(round(world_size_m[1] * pixels_per_meter))

	# Validation override: draw only the uniform field (constant vector), ignore particles
	if getattr(config, "UNIFORM_FIELD_VISUAL_OVERRIDE", False):
		Ex = float(config.UNIFORM_FIELD_VECTOR_NC[0])
		Ey = float(config.UNIFORM_FIELD_VECTOR_NC[1])
		mag = float(np.hypot(Ex, Ey))
		if mag <= 1e-12:
			return
		if config.FIELD_VIS_MODE == "brightness":
			base_r, base_g, base_b = config.COLOR_FIELD_VECTOR
			# Precompute normalized direction and brightness factor
			dir_x = Ex / mag
			dir_y = Ey / mag
			pix_strength = config.FIELD_VECTOR_SCALE * (1 if not config.UNIFORM_FIELD_ACTIVE else 10) * mag
			t = min(1.0, max(0.0, float(config.FIELD_BRIGHTNESS_SCALE * (pix_strength / float(config.FIELD_VECTOR_MAX_LENGTH_PX)))))
			# Arrow geometry (fixed length in brightness mode)
			vec_px = (
				dir_x * float(config.FIELD_FIXED_ARROW_LENGTH_PX),
				dir_y * float(config.FIELD_FIXED_ARROW_LENGTH_PX),
			)
			# Brightness via color mixing
			green_r = int(round(base_r * t))
			green_g = int(round(base_g * t))
			green_b = int(round(base_b * t))
			strength_raw = min(1.0, max(0.0, float(pix_strength / float(config.FIELD_VECTOR_MAX_LENGTH_PX*4.5))))
			wm = strength_raw
			white_r = 255
			white_g = 255
			white_b = 255
			r = int(round(green_r * (1.0 - wm) + white_r * wm))
			g = int(round(green_g * (1.0 - wm) + white_g * wm))
			b = int(round(green_b * (1.0 - wm) + white_b * wm))
			r = max(0, min(255, r))
			g = max(0, min(255, g))
			b = max(0, min(255, b))
			for y in range(grid_step_px // 2, height_px, grid_step_px):
				for x in range(grid_step_px // 2, width_px, grid_step_px):
					_draw_arrow(screen, (r, g, b), (x, y), vec_px, 1e9)
			return
		else:
			# Length mode: arrow length proportional to |E|
			vec_px_base = (Ex * config.FIELD_VECTOR_SCALE * (1 if not config.UNIFORM_FIELD_ACTIVE else 20), Ey * config.FIELD_VECTOR_SCALE * (1 if not config.UNIFORM_FIELD_ACTIVE else 20))
			# Guarantee a minimum visible vector length
			length_px = float(np.hypot(vec_px_base[0], vec_px_base[1]))
			if length_px < 8.0:
				ux = Ex / mag
				uy = Ey / mag
				vec_px_base = (ux * 8.0, uy * 8.0)
			max_length_px = config.FIELD_VECTOR_MAX_LENGTH_PX * 0.6
			for y in range(grid_step_px // 2, height_px, grid_step_px):
				for x in range(grid_step_px // 2, width_px, grid_step_px):
					_draw_arrow(screen, config.COLOR_FIELD_VECTOR, (x, y), vec_px_base, max_length_px)
			return

	if config.FIELD_VIS_MODE == "brightness":
		# Use cached sampler results and draw tinted fixed length arrows with alpha
		sam = _get_sampler(world_size_m, pixels_per_meter, grid_step_px, softening_fraction)
		sam.recompute(particles)
		pairs = sam.iter_centers_and_vectors_px()
		field_surface = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
		base_r, base_g, base_b = config.COLOR_FIELD_VECTOR
		for (x, y), (Ex, Ey) in pairs:
			mag = float(np.hypot(Ex, Ey))
			if mag <= 1e-9:
				continue
			pix_strength = config.FIELD_VECTOR_SCALE * mag
			t = min(1.0, max(0.0, float(config.FIELD_BRIGHTNESS_SCALE * (pix_strength / float(config.FIELD_VECTOR_MAX_LENGTH_PX)))))
			alpha = int(round(255.0 * t))
			if alpha < int(config.FIELD_ALPHA_MIN_DRAW):
				continue
			dir_x = Ex / mag
			dir_y = Ey / mag
			vec_px = (
				dir_x * float(config.FIELD_FIXED_ARROW_LENGTH_PX),
				dir_y * float(config.FIELD_FIXED_ARROW_LENGTH_PX),
			)
			green_r = int(round(base_r * t))
			green_g = int(round(base_g * t))
			green_b = int(round(base_b * t))
			strength_raw = min(1.0, max(0.0, float(pix_strength / float(config.FIELD_VECTOR_MAX_LENGTH_PX*4.5))))
			wm = strength_raw
			white_r = 255
			white_g = 255
			white_b = 255
			r = int(round(green_r * (1.0 - wm) + white_r * wm))
			g = int(round(green_g * (1.0 - wm) + white_g * wm))
			b = int(round(green_b * (1.0 - wm) + white_b * wm))
			r = max(0, min(255, r))
			g = max(0, min(255, g))
			b = max(0, min(255, b))
			rgba = (r, g, b, alpha)
			_draw_arrow(field_surface, rgba, (x, y), vec_px, 1e9)
		screen.blit(field_surface, (0, 0))
		return

	if config.FIELD_SAMPLER_ENABLED:
		sampler = _get_sampler(world_size_m, pixels_per_meter, grid_step_px, softening_fraction)
		sampler.recompute(particles)
		pairs = sampler.iter_centers_and_vectors_px()
		for (x, y), (Ex, Ey) in pairs:
			mag = float(np.hypot(Ex, Ey))
			if mag <= 1e-9:
				continue
			vec_px = (Ex * config.FIELD_VECTOR_SCALE, Ey * config.FIELD_VECTOR_SCALE)
			if config.FIELD_VIS_MODE == "brightness":
				max_length_px = config.FIELD_VECTOR_MAX_LENGTH_PX
			else:
				max_length_px = config.FIELD_VECTOR_MAX_LENGTH_PX * 0.6
			_draw_arrow(screen, config.COLOR_FIELD_VECTOR, (x, y), vec_px, max_length_px)
		return

	for y in range(grid_step_px // 2, height_px, grid_step_px):
		for x in range(grid_step_px // 2, width_px, grid_step_px):
			point_m = np.array([x / pixels_per_meter, y / pixels_per_meter], dtype=float)
			E = electric_field_at_point(point_m, list(particles), world_size_m, softening_fraction)
			mag = float(np.hypot(E[0], E[1]))
			if mag <= 1e-9:
				continue
			vec_px = (E[0] * config.FIELD_VECTOR_SCALE, E[1] * config.FIELD_VECTOR_SCALE)
			if config.FIELD_VIS_MODE == "brightness":
				max_length_px = config.FIELD_VECTOR_MAX_LENGTH_PX
			else:
				max_length_px = config.FIELD_VECTOR_MAX_LENGTH_PX * 0.6
			_draw_arrow(screen, config.COLOR_FIELD_VECTOR, (x, y), vec_px, max_length_px)


