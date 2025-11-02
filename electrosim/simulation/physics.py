from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import os
import numpy as np
try:
	from numba import njit, prange, set_num_threads
	_NUMBA_AVAILABLE = True
	try:
		set_num_threads(max(1, os.cpu_count() or 1))
	except Exception:
		pass
except Exception:
	_NUMBA_AVAILABLE = False
 
from electrosim.config import (
	K_COULOMB,
	COLOR_POSITIVE,
	COLOR_NEGATIVE,
	COLOR_NEUTRAL,
	NEUTRAL_CHARGE_EPS,
)
from electrosim import config as _cfg

if TYPE_CHECKING:
	# Only for type checking, avoids runtime circular imports
	from electrosim.simulation.engine import Particle


def minimum_image_displacement(p_i: np.ndarray, p_j: np.ndarray, world_size_m: np.ndarray) -> np.ndarray:
	"""Compute displacement from i to j using the minimum distance convention in a 2D torus.

	Parameters
	----------
	p_i, p_j : numpy.ndarray shape (2,)
		Positions in meters.
	world_size_m : numpy.ndarray shape (2,)
		World size in meters (width, height).

	Returns
	-------
	numpy.ndarray shape (2,)
		Displacement vector from i to j under minimum-image on the torus.
	"""
	delta = p_j - p_i
	for axis in (0, 1):
		L = world_size_m[axis]
		if delta[axis] > 0.5 * L:
			delta[axis] -= L
		elif delta[axis] < -0.5 * L:
			delta[axis] += L
	return delta


def wrap_position_in_place(pos_m: np.ndarray, world_size_m: np.ndarray) -> None:
	"""Wrap a position into the periodic domain in-place.

	Parameters
	----------
	pos_m : numpy.ndarray shape (2,)
		Position in meters to be wrapped. Modified in-place.
	world_size_m : numpy.ndarray shape (2,)
		World size in meters (width, height).
	"""
	for axis in (0, 1):
		L = world_size_m[axis]
		pos_m[axis] = pos_m[axis] % L


def electric_force_pair(
	p_i: np.ndarray,
	q_i: float,
	r_i: float,
	p_j: np.ndarray,
	q_j: float,
	r_j: float,
	world_size_m: np.ndarray,
	softening_fraction: float,
) -> np.ndarray:
	"""Compute softened Coulomb force on particle i due to j.

	Uses minimum-image displacement on a 2D torus and Plummer-like softening with
	``epsilon = softening_fraction * (r_i + r_j)``.

	Parameters
	----------
	p_i, p_j : numpy.ndarray shape (2,)
		Positions (m) of particles i and j.
	q_i, q_j : float
		Charges (C).
	r_i, r_j : float
		Contact radii (m).
	world_size_m : numpy.ndarray
		World size (m) as (Lx, Ly).
	softening_fraction : float
		Softening fraction applied to contact radius.

	Returns
	-------
	numpy.ndarray shape (2,)
		Force vector on i due to j (N).
	"""
	r_vec = minimum_image_displacement(p_j, p_i, world_size_m)
	r2 = float(np.dot(r_vec, r_vec))
	contact = r_i + r_j
	epsilon = softening_fraction * contact
	# Denominator uses (r^2 + ε^2)^(3/2): since r^3 = (r^2)^(3/2), force is proportional r_vec / r^3
	den = (r2 + epsilon * epsilon) ** 1.5
	if den == 0.0:
		return np.zeros(2, dtype=float)
	coef = K_COULOMB * q_i * q_j / den
	return coef * r_vec


# Numba-accelerated
if _NUMBA_AVAILABLE:

	@njit(cache=True, fastmath=False)
	def _compute_accelerations_numba_serial(
		pos: np.ndarray,
		charge: np.ndarray,
		radius: np.ndarray,
		mass: np.ndarray,
		fixed_mask: np.ndarray,
		world_size: np.ndarray,
		soft_frac: float,
		k_coulomb: float,
		uniform_active_i: int,
		uniform_Ex: float,
		uniform_Ey: float,
	) -> np.ndarray:
		# Particles quantity
		N = pos.shape[0]
		# Accelerations array
		acc = np.zeros((N, 2))
		# World size
		Lx = world_size[0]
		Ly = world_size[1]
		# Compute accelerations for each particle
		for i in range(N):
			# Skip fixed, massless or neutral particles
			if fixed_mask[i] or mass[i] <= 0.0 or charge[i] == 0.0:
				continue
			xi = pos[i, 0]
			yi = pos[i, 1]
			qi = charge[i]
			ri = radius[i]
			fx = 0.0
			fy = 0.0
			for j in range(N):
				if i == j:
					continue
				qj = charge[j]
				if qj == 0.0:
					continue
				dx = xi - pos[j, 0]
				if dx > 0.5 * Lx:
					dx -= Lx
				elif dx < -0.5 * Lx:
					dx += Lx
				dy = yi - pos[j, 1]
				if dy > 0.5 * Ly:
					dy -= Ly
				elif dy < -0.5 * Ly:
					dy += Ly
				r2 = dx * dx + dy * dy
				contact = ri + radius[j]
				eps = soft_frac * contact
				# Denominator (r^2 + ε^2)^(3/2): r^3 = (r^2)^(3/2)
				den = (r2 + eps * eps) ** 1.5
				if den == 0.0:
					continue
				coef = k_coulomb * qi * qj / den
				fx += coef * dx
				fy += coef * dy
			# Uniform field force contribution F = q E
			if uniform_active_i != 0:
				fx += qi * uniform_Ex
				fy += qi * uniform_Ey
			inv_m = 1.0 / mass[i]
			acc[i, 0] = fx * inv_m
			acc[i, 1] = fy * inv_m
		return acc

	@njit(cache=True, fastmath=False)
	def _compute_accelerations_numba_parallel(
		pos: np.ndarray,
		charge: np.ndarray,
		radius: np.ndarray,
		mass: np.ndarray,
		fixed_mask: np.ndarray,
		world_size: np.ndarray,
		soft_frac: float,
		k_coulomb: float,
		uniform_active_i: int,
		uniform_Ex: float,
		uniform_Ey: float,
	) -> np.ndarray:
		N = pos.shape[0]
		acc = np.zeros((N, 2))
		Lx = world_size[0]
		Ly = world_size[1]
		for i in prange(N):
			if fixed_mask[i] or mass[i] <= 0.0 or charge[i] == 0.0:
				continue
			xi = pos[i, 0]
			yi = pos[i, 1]
			qi = charge[i]
			ri = radius[i]
			fx = 0.0
			fy = 0.0
			for j in range(N):
				if i == j:
					continue
				qj = charge[j]
				if qj == 0.0:
					continue
				dx = xi - pos[j, 0]
				if dx > 0.5 * Lx:
					dx -= Lx
				elif dx < -0.5 * Lx:
					dx += Lx
				dy = yi - pos[j, 1]
				if dy > 0.5 * Ly:
					dy -= Ly
				elif dy < -0.5 * Ly:
					dy += Ly
				r2 = dx * dx + dy * dy
				contact = ri + radius[j]
				eps = soft_frac * contact
				den = (r2 + eps * eps) ** 1.5
				if den == 0.0:
					continue
				coef = k_coulomb * qi * qj / den
				fx += coef * dx
				fy += coef * dy
			# Uniform field force contribution F = q E
			if uniform_active_i != 0:
				fx += qi * uniform_Ex
				fy += qi * uniform_Ey
			inv_m = 1.0 / mass[i]
			acc[i, 0] = fx * inv_m
			acc[i, 1] = fy * inv_m
		return acc

	@njit(cache=True, fastmath=False)
	def _compute_field_grid_numba(
		centers_m: np.ndarray,
		pos: np.ndarray,
		charge: np.ndarray,
		radius: np.ndarray,
		world_size: np.ndarray,
		soft_frac: float,
		k_coulomb: float,
	) -> np.ndarray:
		M = centers_m.shape[0]
		N = pos.shape[0]
		out = np.zeros((M, 2))
		Lx = world_size[0]
		Ly = world_size[1]
		for m in prange(M):
			px = centers_m[m, 0]
			py = centers_m[m, 1]
			Ex = 0.0
			Ey = 0.0
			for idx in range(N):
				q = charge[idx]
				if q == 0.0:
					continue
				dx = px - pos[idx, 0]
				if dx > 0.5 * Lx:
					dx -= Lx
				elif dx < -0.5 * Lx:
					dx += Lx
				dy = py - pos[idx, 1]
				if dy > 0.5 * Ly:
					dy -= Ly
				elif dy < -0.5 * Ly:
					dy += Ly
				r2 = dx * dx + dy * dy
				eps = soft_frac * radius[idx]
				den = (r2 + eps * eps) ** 1.5
				if den == 0.0:
					continue
				coef = k_coulomb * q / den
				Ex += coef * dx
				Ey += coef * dy
			out[m, 0] = Ex
			out[m, 1] = Ey
		return out

	@njit(cache=True, fastmath=False)
	def _electric_field_at_point_numba(point: np.ndarray, pos: np.ndarray, charge: np.ndarray, radius: np.ndarray, world_size: np.ndarray, soft_frac: float, k_coulomb: float) -> np.ndarray:
		Ex = 0.0
		Ey = 0.0
		Lx = world_size[0]
		Ly = world_size[1]
		px = point[0]
		py = point[1]
		N = pos.shape[0]
		for idx in range(N):
			q = charge[idx]
			if q == 0.0:
				continue
			dx = px - pos[idx, 0]
			if dx > 0.5 * Lx:
				dx -= Lx
			elif dx < -0.5 * Lx:
				dx += Lx
			dy = py - pos[idx, 1]
			if dy > 0.5 * Ly:
				dy -= Ly
			elif dy < -0.5 * Ly:
				dy += Ly
			r2 = dx * dx + dy * dy
			eps = soft_frac * radius[idx]
			# Same (r^2 + ε^2)^(3/2)
			den = (r2 + eps * eps) ** 1.5
			if den == 0.0:
				continue
			coef = k_coulomb * q / den
			Ex += coef * dx
			Ey += coef * dy
		return np.array([Ex, Ey])


def compute_accelerations(particles: List["Particle"], world_size_m: np.ndarray, softening_fraction: float) -> np.ndarray:
	"""Compute accelerations for all particles from Coulomb forces.

	Fixed, massless or neutral particles get zero acceleration. Uses Numba when
	available; falls back to pure Python otherwise.

	Parameters
	----------
	particles : list[Particle]
		Particle list with positions (m), velocities (m/s), masses (kg), charges (C), radii (m).
	world_size_m : numpy.ndarray shape (2,)
		World size (m) as (Lx, Ly).
	softening_fraction : float
		Softening fraction applied to contact radius in pairwise force.

	Returns
	-------
	numpy.ndarray shape (N, 2)
		Accelerations (m/s^2) for each particle.
	"""
	N = len(particles)
	if N == 0:
		return np.zeros((0, 2), dtype=float)
	if _NUMBA_AVAILABLE:
		pos = np.empty((N, 2), dtype=np.float64)
		charge = np.empty((N,), dtype=np.float64)
		radius = np.empty((N,), dtype=np.float64)
		mass = np.empty((N,), dtype=np.float64)
		fixed_mask = np.empty((N,), dtype=np.bool_)
		for i, p in enumerate(particles):
			pos[i, 0] = float(p.pos_m[0])
			pos[i, 1] = float(p.pos_m[1])
			charge[i] = float(p.charge_c)
			radius[i] = float(p.radius_m)
			mass[i] = float(p.mass_kg)
			fixed_mask[i] = bool(p.fixed)
		world_size = np.array([float(world_size_m[0]), float(world_size_m[1])], dtype=np.float64)
		# Uniform field controls
		uniform_active_i = 1 if bool(_cfg.UNIFORM_FIELD_ACTIVE) else 0
		uniform_Ex = float(_cfg.UNIFORM_FIELD_VECTOR_NC[0]) if uniform_active_i else 0.0
		uniform_Ey = float(_cfg.UNIFORM_FIELD_VECTOR_NC[1]) if uniform_active_i else 0.0
		if _cfg.NUMBA_PARALLEL_ACCEL:
			acc = _compute_accelerations_numba_parallel(
				pos, charge, radius, mass, fixed_mask, world_size,
				float(softening_fraction), float(K_COULOMB),
				int(uniform_active_i), float(uniform_Ex), float(uniform_Ey)
			)
		else:
			acc = _compute_accelerations_numba_serial(
				pos, charge, radius, mass, fixed_mask, world_size,
				float(softening_fraction), float(K_COULOMB),
				int(uniform_active_i), float(uniform_Ex), float(uniform_Ey)
			)
		return acc
	
	# Fallback, just python interpreter
	acc = np.zeros((N, 2), dtype=float)
	for i in range(N):
		pi = particles[i]
		if pi.fixed or pi.mass_kg <= 0.0 or pi.charge_c == 0.0:
			continue
		f_i = np.zeros(2, dtype=float)
		for j in range(N):
			if i == j:
				continue
			pj = particles[j]
			if pj.charge_c == 0.0:
				continue
			f_i += electric_force_pair(
				pi.pos_m, pi.charge_c, pi.radius_m,
				pj.pos_m, pj.charge_c, pj.radius_m,
				world_size_m, softening_fraction,
			)
		# Uniform field force contribution: F = q E
		if bool(_cfg.UNIFORM_FIELD_ACTIVE):
			f_i[0] += float(pi.charge_c) * float(_cfg.UNIFORM_FIELD_VECTOR_NC[0])
			f_i[1] += float(pi.charge_c) * float(_cfg.UNIFORM_FIELD_VECTOR_NC[1])
		acc[i] = f_i / pi.mass_kg
	return acc


def total_kinetic_energy(particles: List["Particle"]) -> float:
	"""Compute total kinetic energy for mobile particles.

	Parameters
	----------
	particles : list[Particle]
		Particles.

	Returns
	-------
	float
		Total kinetic energy (J) excluding fixed particles.
	"""
	E = 0.0
	for p in particles:
		if p.fixed:
			continue
		E += 0.5 * p.mass_kg * float(np.dot(p.vel_mps, p.vel_mps))
	return E


def total_potential_energy(particles: List["Particle"], world_size_m: np.ndarray) -> float:
	"""Compute pairwise Coulomb potential with minimum-image and singularity guard.

	Note: No softening is applied to the potential; instead, a small-distance
	clamp `max(r, 1e-6)` is used. See documentation for rationale.

	Parameters
	----------
	particles : list[Particle]
		Particles.
	world_size_m : numpy.ndarray shape (2,)
		World size (m).

	Returns
	-------
	float
		Total potential energy (J).
	"""
	E = 0.0
	N = len(particles)
	for i in range(N):
		pi = particles[i]
		for j in range(i + 1, N):
			pj = particles[j]
			r_vec = minimum_image_displacement(pi.pos_m, pj.pos_m, world_size_m)
			r = float(np.hypot(r_vec[0], r_vec[1]))

			# Avoid singularity at extremely small r
			r_eff = max(r, 1e-6)
			if r_eff == 0.0:
				continue
			E += K_COULOMB * pi.charge_c * pj.charge_c / r_eff
	return E


def electric_field_at_point(point_m: np.ndarray, particles: List["Particle"], world_size_m: np.ndarray, softening_fraction: float) -> np.ndarray:
	"""Compute electric field vector at a world point from all particles.

	Softened per-source radius using ``epsilon_j = softening_fraction * r_j``.

	Parameters
	----------
	point_m : numpy.ndarray shape (2,)
		Observation point (m).
	particles : list[Particle]
		Particles.
	world_size_m : numpy.ndarray shape (2,)
		World size (m).
	softening_fraction : float
		Softening fraction per source radius.

	Returns
	-------
	numpy.ndarray shape (2,)
		Electric field (N/C) at the observation point.
	"""
	if _NUMBA_AVAILABLE:
		N = len(particles)
		if N == 0:
			return np.zeros(2, dtype=float)
		pos = np.empty((N, 2), dtype=np.float64)
		charge = np.empty((N,), dtype=np.float64)
		radius = np.empty((N,), dtype=np.float64)
		for i, p in enumerate(particles):
			pos[i, 0] = float(p.pos_m[0])
			pos[i, 1] = float(p.pos_m[1])
			charge[i] = float(p.charge_c)
			radius[i] = float(p.radius_m)
		world_size = np.array([float(world_size_m[0]), float(world_size_m[1])], dtype=np.float64)
		point = np.array([float(point_m[0]), float(point_m[1])], dtype=np.float64)
		return _electric_field_at_point_numba(point, pos, charge, radius, world_size, float(softening_fraction), float(K_COULOMB))
	
	# Fallback to python interpreter
	E = np.zeros(2, dtype=float)
	for p in particles:
		if p.charge_c == 0.0:
			continue
		# Vector from source charge to observation point
		r_vec = minimum_image_displacement(p.pos_m, point_m, world_size_m)
		r2 = float(np.dot(r_vec, r_vec))
		epsilon = softening_fraction * p.radius_m
		
		# (r^2 + ε^2)^(3/2) = r^3 with softening
		den = (r2 + epsilon * epsilon) ** 1.5
		if den == 0.0:
			continue
		E += K_COULOMB * p.charge_c * r_vec / den
	return E


def rk4_integrate(particles: List["Particle"], world_size_m: np.ndarray, dt_s: float, softening_fraction: float) -> None:
	"""Advance non-fixed particles using classical RK4.

	Accelerations derive from current positions at each stage; state is
	temporarily updated during stage evaluations and restored before final write.
	Only non-fixed particles are updated.

	Parameters
	----------
	particles : list[Particle]
		Particles to integrate.
	world_size_m : numpy.ndarray shape (2,)
		World size (m).
	dt_s : float
		Time step per substep (s).
	softening_fraction : float
		Softening fraction passed to acceleration computation.
	"""
	if len(particles) == 0:
		return

	# Pack positions and velocities
	pos0 = np.stack([p.pos_m.copy() for p in particles], axis=0)  # (N,2)
	vel0 = np.stack([p.vel_mps.copy() for p in particles], axis=0)  # (N,2)
	fixed_mask = np.array([p.fixed for p in particles], dtype=bool)

	def set_positions_and_velocities_meters(positions: np.ndarray, velocities: np.ndarray) -> None:
		for idx, p in enumerate(particles):
			p.pos_m = positions[idx]
			p.vel_mps = velocities[idx]

	def accelerations_for_positions(positions: np.ndarray, velocities: np.ndarray) -> np.ndarray:
		# Set temporary state, compute accelerations, return
		set_positions_and_velocities_meters(positions, velocities)
		return compute_accelerations(particles, world_size_m, softening_fraction)

	# k1
	a1 = accelerations_for_positions(pos0, vel0)
	k1_v = a1
	k1_x = vel0
	# k2
	pos_k2 = pos0 + 0.5 * dt_s * k1_x
	vel_k2 = vel0 + 0.5 * dt_s * k1_v
	a2 = accelerations_for_positions(pos_k2, vel_k2)
	k2_v = a2
	k2_x = vel_k2
	# k3
	pos_k3 = pos0 + 0.5 * dt_s * k2_x
	vel_k3 = vel0 + 0.5 * dt_s * k2_v
	a3 = accelerations_for_positions(pos_k3, vel_k3)
	k3_v = a3
	k3_x = vel_k3
	# k4
	pos_k4 = pos0 + dt_s * k3_x
	vel_k4 = vel0 + dt_s * k3_v
	a4 = accelerations_for_positions(pos_k4, vel_k4)
	k4_v = a4
	k4_x = vel_k4

	# Combine
	pos_new = pos0 + (dt_s / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
	vel_new = vel0 + (dt_s / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v)

	# Restore original state before writing back
	set_positions_and_velocities_meters(pos0, vel0)

	# Write back only for non-fixed particles
	for idx, p in enumerate(particles):
		if fixed_mask[idx]:
			continue
		p.pos_m = pos_new[idx]
		p.vel_mps = vel_new[idx]


def resolve_collisions(particles: List["Particle"], world_size_m: np.ndarray) -> None:
	"""Resolve merges (opposite charges) and elastic collisions.

	Two-phase handling:
	1) Merge phase for overlapping opposite-charge pairs: conserve mass, charge,
	   and momentum (if not fixed); area-equivalent radius; history merge; id reassign.
	2) Elastic phase for remaining overlaps: positional correction along normal,
	   then 1D normal impulse with restitution e=1. Fixed treated as infinite mass.

	Parameters
	----------
	particles : list[Particle]
		Mutable particle list.
	world_size_m : numpy.ndarray shape (2,)
		World size (m) for displacement and wrapping.
	"""
	N = len(particles)
	if N <= 1:
		return
	removed: set[int] = set()
	to_delete: list[int] = []

	# Handle sticky merges for opposite charges
	for i in range(N):
		if i in removed:
			continue
		pi = particles[i]
		for j in range(i + 1, N):
			if j in removed:
				continue
			pj = particles[j]
			r_vec = minimum_image_displacement(pi.pos_m, pj.pos_m, world_size_m)
			dist = float(np.hypot(r_vec[0], r_vec[1]))
			r_contact = pi.radius_m + pj.radius_m
			if dist >= r_contact or dist == 0.0:
				continue
			# Opposite charges stick
			if pi.charge_c * pj.charge_c < 0.0:
				m1 = pi.mass_kg
				m2 = pj.mass_kg
				total_m = m1 + m2
				q_new = pi.charge_c + pj.charge_c
				r_new = float(np.sqrt(pi.radius_m * pi.radius_m + pj.radius_m * pj.radius_m))
				fixed_new = pi.fixed or pj.fixed
				if fixed_new:
					# Stick to the fixed particle position, velocity zero
					pos_new = pj.pos_m.copy() if pj.fixed else pi.pos_m.copy()
					vel_new = np.zeros(2, dtype=float)
				else:
					pos_new = pi.pos_m + r_vec * (m2 / total_m)
					vel_new = (m1 * pi.vel_mps + m2 * pj.vel_mps) / total_m
				
				# Write into i, mark j for deletion
				pi.mass_kg = total_m
				pi.charge_c = q_new
				pi.radius_m = r_new
				pi.fixed = fixed_new
				pi.pos_m = pos_new
				pi.vel_mps = vel_new

				if abs(q_new) <= NEUTRAL_CHARGE_EPS:
					pi.color_rgb = COLOR_NEUTRAL
				else:
					pi.color_rgb = COLOR_POSITIVE if q_new > 0.0 else COLOR_NEGATIVE
				
				# Merge histories
				keep_history = pi.history
				if m2 > m1 or (m2 == m1 and len(pj.history) > len(pi.history)):
					keep_history = pj.history
				pi.history = keep_history

				last_t = pi.history[-1][0] if pi.history else 0.0
				pi.history.append((last_t, (float(pi.pos_m[0]), float(pi.pos_m[1]))))
				wrap_position_in_place(pi.pos_m, world_size_m)
				removed.add(j)
				to_delete.append(j)
				continue

	# Delete merged particles
	if to_delete:
		for idx in sorted(to_delete, reverse=True):
			if 0 <= idx < len(particles):
				del particles[idx]
		# Reassign ids
		for idx, p in enumerate(particles):
			p.id = idx

	# Resolve elastic collisions for remaining pairs
	N2 = len(particles)
	processed: set[Tuple[int, int]] = set()
	for i in range(N2):
		pi = particles[i]
		for j in range(i + 1, N2):
			if (i, j) in processed:
				continue
			pj = particles[j]
			r_vec = minimum_image_displacement(pi.pos_m, pj.pos_m, world_size_m)
			dist = float(np.hypot(r_vec[0], r_vec[1]))
			r_contact = pi.radius_m + pj.radius_m
			if dist >= r_contact or dist == 0.0:
				continue
			
			# Normal unit vector from i to j
			n = r_vec / dist

			# Positional correction to separate overlap
			penetration = r_contact - dist
			if pi.fixed and pj.fixed:
				pass
			elif pi.fixed:
				pj.pos_m += n * penetration
			elif pj.fixed:
				pi.pos_m -= n * penetration
			else:
				m1 = pi.mass_kg
				m2 = pj.mass_kg
				total = m1 + m2
				if total > 0.0:
					pi.pos_m -= n * (penetration * (m2 / total))
					pj.pos_m += n * (penetration * (m1 / total))

			v_rel = pj.vel_mps - pi.vel_mps
			v_rel_n = float(np.dot(v_rel, n))
			if v_rel_n > 0:
				processed.add((i, j))
				continue

			restitution = 1.0
			if pi.fixed and pj.fixed:
				processed.add((i, j))
				continue
			elif pi.fixed:
				m1 = float("inf")
				m2 = pj.mass_kg
			elif pj.fixed:
				m1 = pi.mass_kg
				m2 = float("inf")
			else:
				m1 = pi.mass_kg
				m2 = pj.mass_kg

			inv_m1 = 0.0 if not np.isfinite(m1) else 1.0 / m1
			inv_m2 = 0.0 if not np.isfinite(m2) else 1.0 / m2
			j_impulse = -(1.0 + restitution) * v_rel_n / (inv_m1 + inv_m2)
			impulse_vec = j_impulse * n
			if np.isfinite(m1):
				pi.vel_mps -= impulse_vec * inv_m1
			if np.isfinite(m2):
				pj.vel_mps += impulse_vec * inv_m2
			processed.add((i, j))

