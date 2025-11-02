from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional, Tuple

import numpy as np

from electrosim import config
from electrosim.simulation.physics import (
	compute_accelerations,
	minimum_image_displacement,
	resolve_collisions,
	rk4_integrate, 
	total_kinetic_energy,
	total_potential_energy,
	wrap_position_in_place,
)


@dataclass
class Particle:
	"""Simulated charged particle in a 2D periodic domain.

	Attributes
	----------
	id : int
		Unique identifier within the current particle list.
	pos_m : numpy.ndarray shape (2,)
		Position in meters.
	vel_mps : numpy.ndarray shape (2,)
		Velocity in meters per second.
	mass_kg : float
		Mass in kilograms.
	charge_c : float
		Charge in Coulombs.
	radius_m : float
		Collision/visual radius in meters.
	fixed : bool
		If True, particle does not move (treated as infinite mass during collisions).
	color_rgb : tuple[int, int, int]
		Display color based on charge sign or neutrality.
	history : collections.deque[(float, (float, float))]
		Time-stamped positions for trajectory rendering.
	"""
	id: int
	pos_m: np.ndarray
	vel_mps: np.ndarray
	mass_kg: float
	charge_c: float
	radius_m: float
	fixed: bool = False
	color_rgb: Tuple[int, int, int] = (255, 255, 255)
	history: Deque[Tuple[float, Tuple[float, float]]] = field(default_factory=lambda: deque(maxlen=50000))


class Simulation:
	"""Simulation orchestrator for N-body Coulomb dynamics.

	Drives particles and world parameters, advances time, computes energies,
	maintains selection and visualization state, and exposes frame/substep
	stepping consistent with the rendering loop.
	"""
	def __init__(self) -> None:
		"""Initialize a new simulation with default settings and one center particle.

		Creates the world size from config, initializes UI/visualization flags,
		energies, simulation time, and warms Numba acceleration path if available.
		"""
		self.world_size_m = np.array([config.WORLD_WIDTH_M, config.WORLD_HEIGHT_M], dtype=float)
		self.particles: List[Particle] = []
		self.selected_index: Optional[int] = None
		self.show_field: bool = False
		self.show_forces: bool = False
		self.show_velocities: bool = False
		self.show_trails: bool = True
		self.show_meter_grid: bool = False
		self.paused: bool = False
		self.speed_index: int = 1  # 0.5x, 1x, 2x, 4x at 1x index=1
		self.substeps_base: int = config.SUBSTEPS_BASE_PER_FRAME
		self.energy_kin: float = 0.0
		self.energy_pot: float = 0.0
		self.energy_tot: float = 0.0
		self.t_sim: float = 0.0
		self.last_forces: Optional[np.ndarray] = None
		# Validation state (uniform field case)
		self.validation_active: bool = False
		self.validation_theory_traj: List[Tuple[float, Tuple[float, float]]] = []
		self.validation_current_errors: dict = {}
		self.validation_initial_pos_m: Optional[np.ndarray] = None
		self.validation_initial_vel_mps: Optional[np.ndarray] = None
		self.validation_accel_mps2: Optional[np.ndarray] = None
		self.validation_reached_end: bool = False
		self.validation_final_theory_pos_m: Optional[np.ndarray] = None
		self.validation_final_theory_vel_mps: Optional[np.ndarray] = None
		self.validation_final_sim_pos_m: Optional[np.ndarray] = None
		self.validation_final_sim_vel_mps: Optional[np.ndarray] = None
		self.reset_to_default_scene()
		# Pre-compile function with Numba at startup
		try:
			_ = compute_accelerations(self.particles, self.world_size_m, config.SOFTENING_FRACTION)
		except Exception:
			pass

	def reset_to_default_scene(self) -> None:
		"""Reset to a single particle at world center with default properties.

		Side effects: clears particles and timers, adds a new particle with default
		charge/mass/radius, recomputes energies, and resets selection.
		"""
		self.clear()
		center = np.array([self.world_size_m[0] * 0.5, self.world_size_m[1] * 0.5], dtype=float)
		v0 = np.zeros(2, dtype=float)
		self.add_particle(
			pos_m=center,
			vel_mps=v0,
			charge_c=-config.DEFAULT_CHARGE_C,
			mass_kg=config.DEFAULT_MASS_KG,
			radius_m=config.DEFAULT_RADIUS_M,
			fixed=False,
		)
		self.recompute_energies()

	def clear(self) -> None:
		"""Remove all particles and reset timers, energies, selection, and forces."""
		self.particles.clear()
		self.selected_index = None
		self.t_sim = 0.0
		self.energy_kin = 0.0
		self.energy_pot = 0.0
		self.energy_tot = 0.0
		self.last_forces = None

	def add_particle(
		self,
		pos_m: np.ndarray,
		vel_mps: np.ndarray,
		charge_c: float,
		mass_kg: float,
		radius_m: float,
		fixed: bool,
	) -> None:
		"""Create and append a particle with clamped properties and charge-derived color.

		Parameters
		----------
		pos_m : numpy.ndarray shape (2,)
			Initial position (m).
		vel_mps : numpy.ndarray shape (2,)
			Initial velocity (m/s).
		charge_c : float
			Charge (C), clamped to [`MIN_CHARGE_C`, `MAX_CHARGE_C`].
		mass_kg : float
			Mass (kg), clamped to [`MIN_MASS_KG`, `MAX_MASS_KG`].
		radius_m : float
			Radius (m), clamped to [`MIN_RADIUS_M`, `MAX_RADIUS_M`].
		fixed : bool
			If True, particle starts fixed.
		"""
		if len(self.particles) >= config.MAX_PARTICLES:
			return
		charge_c = float(np.clip(charge_c, config.MIN_CHARGE_C, config.MAX_CHARGE_C))
		mass_kg = float(np.clip(mass_kg, config.MIN_MASS_KG, config.MAX_MASS_KG))
		radius_m = float(np.clip(radius_m, config.MIN_RADIUS_M, config.MAX_RADIUS_M))
		part_id = len(self.particles)
		if abs(charge_c) <= config.NEUTRAL_CHARGE_EPS:
			color = config.COLOR_NEUTRAL
		else:
			color = config.COLOR_POSITIVE if charge_c > 0 else config.COLOR_NEGATIVE
		p = Particle(
			id=part_id,
			pos_m=np.array(pos_m, dtype=float),
			vel_mps=np.array(vel_mps, dtype=float),
			mass_kg=mass_kg,
			charge_c=charge_c,
			radius_m=radius_m,
			fixed=bool(fixed),
			color_rgb=color,
		)
		self.particles.append(p)

	def _update_color(self, p: Particle) -> None:
		"""Update particle display color from its charge with neutral threshold."""
		if abs(p.charge_c) <= config.NEUTRAL_CHARGE_EPS:
			p.color_rgb = config.COLOR_NEUTRAL
		else:
			p.color_rgb = config.COLOR_POSITIVE if p.charge_c > 0 else config.COLOR_NEGATIVE

	def select_particle_at_screen_pos(self, px: int, py: int) -> None:
		"""Select the nearest particle under a screen pixel within a small radius.

		Parameters
		----------
		px, py : int
			Screen pixel coordinates.
		"""
		pixels_per_meter = config.PIXELS_PER_METER
		world_pos = np.array([px / pixels_per_meter, py / pixels_per_meter], dtype=float)
		best_idx: Optional[int] = None
		best_dist_px = 1e9
		for idx, p in enumerate(self.particles):
			dis_p = minimum_image_displacement(world_pos, p.pos_m, self.world_size_m)
			dist_m = float(np.hypot(dis_p[0], dis_p[1]))
			dist_px = dist_m * pixels_per_meter
			r_px = p.radius_m * pixels_per_meter
			if dist_px <= max(6.0, r_px + 6.0) and dist_px < best_dist_px:
				best_dist_px = dist_px
				best_idx = idx
		self.selected_index = best_idx

	def adjust_selected_charge(self, delta_c: float) -> None:
		"""Adjust charge of selected particle by `delta_c` (C), clamped to config range."""
		if self.selected_index is None:
			return
		p = self.particles[self.selected_index]
		p.charge_c = float(np.clip(p.charge_c + delta_c, config.MIN_CHARGE_C, config.MAX_CHARGE_C))
		self._update_color(p)

	def adjust_selected_mass(self, delta_kg: float) -> None:
		"""Adjust mass of selected particle by `delta_kg` (kg), clamped to config range."""
		if self.selected_index is None:
			return
		p = self.particles[self.selected_index]
		p.mass_kg = float(np.clip(p.mass_kg + delta_kg, config.MIN_MASS_KG, config.MAX_MASS_KG))

	def adjust_selected_radius(self, delta_m: float) -> None:
		"""Adjust radius of selected particle by `delta_m` (m), clamped to config range."""
		if self.selected_index is None:
			return
		p = self.particles[self.selected_index]
		p.radius_m = float(np.clip(p.radius_m + delta_m, config.MIN_RADIUS_M, config.MAX_RADIUS_M))

	def toggle_selected_fixed(self) -> None:
		"""Toggle fixed/mobile state of the currently selected particle (if any)."""
		if self.selected_index is None:
			return
		p = self.particles[self.selected_index]
		p.fixed = not p.fixed

	def remove_selected_particle(self) -> None:
		"""Remove the selected particle and reassign sequential `id`s to the remainder."""
		if self.selected_index is None:
			return
		del self.particles[self.selected_index]
		self.selected_index = None
		# Reassign IDs
		for i, p in enumerate(self.particles):
			p.id = i

	def recompute_energies(self) -> None:
		"""Recompute kinetic, potential, and total energies from current state."""
		self.energy_kin = total_kinetic_energy(self.particles)
		self.energy_pot = total_potential_energy(self.particles, self.world_size_m)
		self.energy_tot = self.energy_kin + self.energy_pot

	def _wrap_all_positions(self) -> None:
		"""Wrap all particle positions inside the world bounds (periodic domain)."""
		for p in self.particles:
			wrap_position_in_place(p.pos_m, self.world_size_m)

	def _ensure_selected_valid(self) -> None:
		"""Clear `selected_index` if it no longer points to a valid particle."""
		if self.selected_index is not None and (self.selected_index < 0 or self.selected_index >= len(self.particles)):
			self.selected_index = None

	def _compute_last_forces(self) -> None:
		"""Compute last per-particle forces for visualization.

		Uses `compute_accelerations` times mass for mobile particles; fixed particles
		report zero force.
		"""
		if len(self.particles) == 0:
			self.last_forces = None
			return
		acc = compute_accelerations(self.particles, self.world_size_m, config.SOFTENING_FRACTION)
		self.last_forces = np.stack([
			(acc[i] * (0.0 if self.particles[i].fixed else self.particles[i].mass_kg)) for i in range(len(self.particles))
		], axis=0).reshape((len(self.particles), 2)) if len(self.particles) > 0 else None

	def _advance_time_and_trails(self, dt_s: float) -> None:
		"""Advance simulation clock and update trajectories at a fixed sampling rate.

		Parameters
		----------
		dt_s : float
			Time step increment (s) to add to `t_sim`.
		"""
		self.t_sim += dt_s
		self.update_trails(sample_interval_s=1.0 / float(config.FPS_TARGET))

	def update_trails(self, sample_interval_s: float) -> None:
		"""Append particle positions to trails if `sample_interval_s` has elapsed.

		Old entries older than `TRAJECTORY_HISTORY_SECONDS` are pruned.
		"""
		for p in self.particles:
			if not self.show_trails:
				continue
			if not p.history:
				p.history.append((self.t_sim, (float(p.pos_m[0]), float(p.pos_m[1]))))
				continue
			last_t = p.history[-1][0]
			if self.t_sim - last_t >= sample_interval_s:
				p.history.append((self.t_sim, (float(p.pos_m[0]), float(p.pos_m[1]))))

			# Purge old
			while p.history and (self.t_sim - p.history[0][0] > config.TRAJECTORY_HISTORY_SECONDS):
				p.history.popleft()

	def step_substep(self, dt_s: float) -> None:
		"""Advance the simulation by one substep of duration `dt_s`.

		Performs RK4 integration, wraps positions, resolves collisions, wraps again,
		and validates selection index.
		"""
		if self.paused:
			return

		# Integrate motion using RK4
		rk4_integrate(self.particles, self.world_size_m, dt_s, config.SOFTENING_FRACTION)
		self._wrap_all_positions()
		resolve_collisions(self.particles, self.world_size_m)
		self._wrap_all_positions()
		self._ensure_selected_valid()

	def step_frame(self) -> None:
		"""Advance the simulation by a frame worth of substeps based on speed.

		Runs physics integration per substep, then once-per-frame visual-only work:
		trails, energies, and force caching (optional). `t_sim` accumulates substep
		time.
		"""
		if self.paused:
			return
		mult = config.SPEED_MULTIPLIERS[self.speed_index]
		substeps = max(1, int(self.substeps_base * mult))
		dt_s = config.DT_S
		for _ in range(substeps):
			self.step_substep(dt_s)
			self.t_sim += dt_s
		# Once per frame: update trails, energies, and optional forces for visualization
		if self.show_trails:
			self.update_trails(sample_interval_s=1.0 / float(config.FPS_TARGET))
		self.recompute_energies()
		if self.show_forces:
			self._compute_last_forces()
		else:
			self.last_forces = None

		# Update validation per-frame errors
		if self.validation_active:
			try:
				# Only defined for single-particle validation
				if len(self.particles) >= 1 and self.validation_initial_pos_m is not None and self.validation_initial_vel_mps is not None and self.validation_accel_mps2 is not None:
					t_eval = min(float(self.t_sim), float(config.VALIDATION_DURATION_S))
					x0 = self.validation_initial_pos_m
					v0 = self.validation_initial_vel_mps
					a = self.validation_accel_mps2
					pos_theory = x0 + v0 * t_eval + 0.5 * a * (t_eval * t_eval)
					# Wrap theoretical position for comparison/drawing
					pos_theory = pos_theory.copy()
					wrap_position_in_place(pos_theory, self.world_size_m)
					vel_theory = v0 + a * t_eval
					p = self.particles[0]
					# Minimum-image displacement for position error
					dpos = minimum_image_displacement(pos_theory, p.pos_m, self.world_size_m)
					pos_err = float(np.hypot(dpos[0], dpos[1]))
					v_diff = vel_theory - p.vel_mps
					vel_err = float(np.hypot(v_diff[0], v_diff[1]))
					self.validation_current_errors = {
						"t": float(t_eval),
						"pos_err": float(pos_err),
						"vel_err": float(vel_err),
					}
			except Exception:
				pass

			# Pause and capture final comparison exactly at end time
			if (not self.validation_reached_end) and (self.t_sim >= float(config.VALIDATION_DURATION_S)):
				try:
					t_end = float(config.VALIDATION_DURATION_S)
					# Compute theory at t_end
					x0 = self.validation_initial_pos_m if self.validation_initial_pos_m is not None else np.zeros(2, dtype=float)
					v0 = self.validation_initial_vel_mps if self.validation_initial_vel_mps is not None else np.zeros(2, dtype=float)
					a = self.validation_accel_mps2 if self.validation_accel_mps2 is not None else np.zeros(2, dtype=float)
					pos_th = x0 + v0 * t_end + 0.5 * a * (t_end * t_end)
					pos_th = pos_th.copy()
					wrap_position_in_place(pos_th, self.world_size_m)
					vel_th = v0 + a * t_end
					self.validation_final_theory_pos_m = pos_th
					self.validation_final_theory_vel_mps = vel_th
					# Read sim
					if len(self.particles) >= 1:
						p0 = self.particles[0]
						self.validation_final_sim_pos_m = p0.pos_m.copy()
						self.validation_final_sim_vel_mps = p0.vel_mps.copy()
					# Update errors at final time
					dpos = minimum_image_displacement(self.validation_final_theory_pos_m, self.validation_final_sim_pos_m, self.world_size_m) if (self.validation_final_theory_pos_m is not None and self.validation_final_sim_pos_m is not None) else np.zeros(2)
					pos_err = float(np.hypot(dpos[0], dpos[1]))
					v_diff = (self.validation_final_theory_vel_mps - self.validation_final_sim_vel_mps) if (self.validation_final_theory_vel_mps is not None and self.validation_final_sim_vel_mps is not None) else np.zeros(2)
					vel_err = float(np.hypot(v_diff[0], v_diff[1]))
					self.validation_current_errors = {"t": t_end, "pos_err": pos_err, "vel_err": vel_err}
					# Print comparison
					print("\nUniform field validation - FINAL at t=%.3f s" % t_end)
					print("theory: pos=(%.6f, %.6f) m, vel=(%.6f, %.6f) m/s" % (pos_th[0], pos_th[1], vel_th[0], vel_th[1]))
					if self.validation_final_sim_pos_m is not None and self.validation_final_sim_vel_mps is not None:
						ps = self.validation_final_sim_pos_m
						vs = self.validation_final_sim_vel_mps
						print("  sim : pos=(%.6f, %.6f) m, vel=(%.6f, %.6f) m/s" % (ps[0], ps[1], vs[0], vs[1]))
					print("errors: |pos|=%.6e m, |vel|=%.6e m/s" % (pos_err, vel_err))
					self.validation_reached_end = True
					self.paused = True
				except Exception:
					self.validation_reached_end = True

	def start_uniform_field_validation(self) -> None:
		"""Set up and launch the uniform-field validation scenario.

		Creates a single particle at the world center with zero initial velocity,
		enables a constant uniform field for both physics and visualization, precomputes
		the analytical trajectory, and prints
		a summary table. Runtime errors vs analytical are updated each frame.
		"""
		# Reset validation state for a fresh run
		self.validation_active = False
		self.validation_reached_end = False
		self.validation_theory_traj = []
		self.validation_current_errors = {}
		self.validation_final_theory_pos_m = None
		self.validation_final_theory_vel_mps = None
		self.validation_final_sim_pos_m = None
		self.validation_final_sim_vel_mps = None

		# Clear scene and add one particle at center
		self.clear()
		center = np.array([self.world_size_m[0] * 0.5, self.world_size_m[1] * 0.5], dtype=float)
		v0 = np.zeros(2, dtype=float)
		self.add_particle(
			pos_m=center,
			vel_mps=v0,
			charge_c=config.DEFAULT_CHARGE_C,
			mass_kg=config.DEFAULT_MASS_KG,
			radius_m=config.DEFAULT_RADIUS_M,
			fixed=False,
		)
		self.selected_index = 0
		self.t_sim = 0.0

		# Enable uniform field and visualization override
		config.UNIFORM_FIELD_ACTIVE = True
		config.UNIFORM_FIELD_VISUAL_OVERRIDE = True
		self.show_field = True
		self.show_trails = True
		self.paused = False

		# Store initial conditions and constant acceleration a = (q/m) E
		p = self.particles[0]
		self.validation_initial_pos_m = p.pos_m.copy()
		self.validation_initial_vel_mps = p.vel_mps.copy()
		E = np.array([float(config.UNIFORM_FIELD_VECTOR_NC[0]), float(config.UNIFORM_FIELD_VECTOR_NC[1])], dtype=float)
		if p.mass_kg > 0.0:
			self.validation_accel_mps2 = (p.charge_c / p.mass_kg) * E
		else:
			self.validation_accel_mps2 = np.zeros(2, dtype=float)

		# Precompute theoretical trajectory sampled at FPS cadence
		dur = float(config.VALIDATION_DURATION_S)
		dt_sample = 1.0 / float(config.FPS_TARGET)
		t_theory: List[Tuple[float, Tuple[float, float]]] = []
		t = 0.0
		while t < dur + 1e-9:
			pos = self.validation_initial_pos_m + self.validation_initial_vel_mps * t + 0.5 * self.validation_accel_mps2 * (t * t)
			pos = pos.copy()
			wrap_position_in_place(pos, self.world_size_m)
			t_theory.append((float(t), (float(pos[0]), float(pos[1]))))
			t += dt_sample
		self.validation_theory_traj = t_theory

		self.validation_active = True
		self.validation_current_errors = {"t": 0.0, "pos_err": 0.0, "vel_err": 0.0}

	def stop_validation(self) -> None:
		"""Disable uniform-field validation and restore defaults."""
		self.validation_active = False
		self.validation_theory_traj = []
		self.validation_dt_sweep_results = []
		self.validation_current_errors = {}
		self.validation_initial_pos_m = None
		self.validation_initial_vel_mps = None
		self.validation_accel_mps2 = None
		config.UNIFORM_FIELD_ACTIVE = False
		config.UNIFORM_FIELD_VISUAL_OVERRIDE = False
