from __future__ import annotations

from typing import Iterable, Optional

import numpy as np
import pygame

from electrosim import config
from electrosim.simulation.engine import Particle
from electrosim.rendering.primitives import world_vector_to_screen, _draw_arrow, draw_glow_at_screen_pos
 

def draw_particles(screen: pygame.Surface, particles: Iterable[Particle], pixels_per_meter: float, selected_index: Optional[int]) -> None:
	"""Draw particles as filled circles with optional borders for fixed/selected.

	Parameters
	----------
	screen : pygame.Surface
		Target surface.
	particles : Iterable[Particle]
		Particles to draw.
	pixels_per_meter : float
		Scaling from meters to pixels.
	selected_index : int | None
		Index of selected particle in list order, if any.
	"""
	for idx, p in enumerate(particles):
		center = world_vector_to_screen(p.pos_m, pixels_per_meter)
		r_px = max(2, int(round(p.radius_m * pixels_per_meter)))
		pygame.draw.circle(screen, p.color_rgb, center, r_px)
		border_color = None
		if p.fixed:
			border_color = config.COLOR_FIXED_BORDER
		if selected_index is not None and idx == selected_index:
			border_color = config.COLOR_SELECTED_BORDER
		if border_color is not None:
			pygame.draw.circle(screen, border_color, center, r_px, 2)


def draw_velocity_vectors(screen: pygame.Surface, particles: Iterable[Particle], pixels_per_meter: float) -> None:
	"""Draw velocity arrows scaled by a constant factor.

	Parameters
	----------
	screen : pygame.Surface
		Target surface.
	particles : Iterable[Particle]
		Particles to draw velocity for.
	pixels_per_meter : float
		Scaling from meters to pixels.
	"""
	for p in particles:
		start = world_vector_to_screen(p.pos_m, pixels_per_meter)
		vec = (p.vel_mps[0] * config.VELOCITY_VECTOR_SCALE, p.vel_mps[1] * config.VELOCITY_VECTOR_SCALE)
		_draw_arrow(screen, config.COLOR_VELOCITY_VECTOR, start, vec, config.VECTOR_MAX_LENGTH_PX)


def draw_force_vectors(screen: pygame.Surface, particles: Iterable[Particle], forces_array: Optional[np.ndarray], pixels_per_meter: float) -> None:
	"""Draw force arrows per particle using precomputed forces if available.

	Parameters
	----------
	screen : pygame.Surface
		Target surface.
	particles : Iterable[Particle]
		Particles to draw forces for.
	forces_array : numpy.ndarray | None
		Per-particle forces (N) shaped (N,2). If None, nothing is drawn.
	pixels_per_meter : float
		Scaling from meters to pixels.
	"""
	if forces_array is None:
		return
	for i, p in enumerate(particles):
		start = world_vector_to_screen(p.pos_m, pixels_per_meter)
		f = forces_array[i] if i < len(forces_array) else np.zeros(2)
		vec = (f[0] * config.FORCE_VECTOR_SCALE, f[1] * config.FORCE_VECTOR_SCALE)
		_draw_arrow(screen, config.COLOR_FORCE_VECTOR, start, vec, config.VECTOR_MAX_LENGTH_PX)


def draw_particle_glows(screen: pygame.Surface, particles: Iterable[Particle], pixels_per_meter: float) -> None:
	"""Draw glows for all non-neutral particles.

	Parameters
	----------
	screen : pygame.Surface
		Target surface.
	particles : Iterable[Particle]
		Particles to draw glow for.
	pixels_per_meter : float
		Scaling from meters to pixels.
	"""
	for p in particles:
		if abs(p.charge_c) <= config.NEUTRAL_CHARGE_EPS:
			continue
		center = world_vector_to_screen(p.pos_m, pixels_per_meter)
		base_radius_px = max(2, int(round(p.radius_m * pixels_per_meter)))
		t = min(1.0, max(0.0, float(abs(p.charge_c) / config.MAX_CHARGE_C)))
		color_rgb = p.color_rgb
		draw_glow_at_screen_pos(screen, center, base_radius_px, color_rgb, t)


