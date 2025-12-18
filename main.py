from __future__ import annotations

import sys
import time

import pygame

from electrosim import config
from electrosim.simulation.engine import Simulation
from electrosim.rendering.draw import (
	draw_field_grid,
	draw_meter_grid,
	draw_force_vectors,
	draw_overlay,
	draw_particle_glows,
	draw_particles,
	draw_trails,
	draw_velocity_vectors,
)
from electrosim.ui.controls import InputState, handle_events, render_placement_preview, render_hover_tooltip
from electrosim.rendering.trails import draw_polyline_world


def main() -> None:
	"""Run the main event loop: handle input, step simulation, and render.

	Initializes Pygame and the window, constructs the `Simulation` and `InputState`,
	and iterates frames by processing input, stepping the simulation by substeps,
	drawing the scene, and overlaying performance and state metrics.
	"""
	pygame.init()
	screen = pygame.display.set_mode((config.WINDOW_WIDTH_PX, config.WINDOW_HEIGHT_PX))
	pygame.display.set_caption("ElectroSim - Charged particle simulator")
	clock = pygame.time.Clock()
	font = pygame.font.SysFont("consolas,sans-serif", 16)
	ppm = config.PIXELS_PER_METER

	sim = Simulation()
	input_state = InputState()

	while True:
		frame_t0 = time.perf_counter()
		# Events and controls
		handle_events(pygame, sim, input_state, ppm)

		# Logic and physics step
		t_ph0 = time.perf_counter()
		sim.step_frame()
		t_ph1 = time.perf_counter()
		physics_ms = (t_ph1 - t_ph0) * 1000.0

		# Drawing
		field_ms = 0.0
		t_draw0 = time.perf_counter()

		draw_force_vectors(screen, sim.particles, sim.last_forces, ppm)
	
		screen.fill(config.COLOR_BG)
		if sim.show_meter_grid:
			draw_meter_grid(screen, sim.world_size_m, ppm)
		if sim.show_field or getattr(sim, "validation_active", False) or getattr(config, "UNIFORM_FIELD_VISUAL_OVERRIDE", False):
			FIELD_GRID_STEP_PX = config.FIELD_GRID_STEP_PX
			if config.FIELD_VIS_MODE != "brightness":
				FIELD_GRID_STEP_PX = int(config.FIELD_GRID_STEP_PX*2.6) 
			t_f0 = time.perf_counter()
			draw_field_grid(screen, sim.particles, sim.world_size_m, ppm, FIELD_GRID_STEP_PX, config.SOFTENING_FRACTION)
			t_f1 = time.perf_counter()
			field_ms += (t_f1 - t_f0) * 1000.0
		# Glow under trajectories and particles
		draw_particle_glows(screen, sim.particles, ppm)
		if sim.show_trails:
			draw_trails(screen, sim.particles, ppm)
		# Theory: draw analytical trajectory when validation is active
		if getattr(sim, "validation_active", False) and sim.validation_theory_traj:
			points = [xy for (_, xy) in sim.validation_theory_traj]
			draw_polyline_world(screen, points, config.COLOR_THEORY_TRAJECTORY, 2, ppm)
		draw_particles(screen, sim.particles, ppm, sim.selected_index)
		if sim.show_velocities:
			draw_velocity_vectors(screen, sim.particles, ppm)
		if sim.show_forces:
			draw_force_vectors(screen, sim.particles, sim.last_forces, ppm)
		render_placement_preview(screen, input_state, ppm)

		t_draw1 = time.perf_counter()
		draw_ms_total = (t_draw1 - t_draw0) * 1000.0
		draw_ms = max(0.0, draw_ms_total - field_ms)

		# Overlay
		fps = clock.get_fps() or float(config.FPS_TARGET)
		speed_label = {0: "0.5×", 1: "1×", 2: "2×", 3: "4×"}[sim.speed_index]
		sim_state = {
			"fps": fps,
			"n": len(sim.particles),
			"speed_label": speed_label,
			"dt_s": config.DT_S,
			"substeps": max(1, int(config.SUBSTEPS_BASE_PER_FRAME * config.SPEED_MULTIPLIERS[sim.speed_index])),
			"E_kin": sim.energy_kin,
			"E_pot": sim.energy_pot,
			"E_tot": sim.energy_tot,
		}
		# Validation overlay payload
		if getattr(sim, "validation_active", False):
			E = (float(config.UNIFORM_FIELD_VECTOR_NC[0]), float(config.UNIFORM_FIELD_VECTOR_NC[1]))
			# Acceleration a = (q/m)E from sim state if available
			if getattr(sim, "validation_accel_mps2", None) is not None:
				a = (float(sim.validation_accel_mps2[0]), float(sim.validation_accel_mps2[1]))
			else:
				a = (0.0, 0.0)
			cur = getattr(sim, "validation_current_errors", {}) or {}
			val_payload = {
				"active": True,
				"E": E,
				"a": a,
				"t": float(cur.get("t", 0.0)),
				"pos_err": float(cur.get("pos_err", 0.0)),
				"vel_err": float(cur.get("vel_err", 0.0)),
				"dt_s": float(config.DT_S),
				"duration_s": float(getattr(config, "VALIDATION_DURATION_S", 0.0)),
			}
			# Final comparison values
			val_payload["reached_end"] = bool(getattr(sim, "validation_reached_end", False))
			pos_th = getattr(sim, "validation_final_theory_pos_m", None)
			vel_th = getattr(sim, "validation_final_theory_vel_mps", None)
			pos_sim = getattr(sim, "validation_final_sim_pos_m", None)
			vel_sim = getattr(sim, "validation_final_sim_vel_mps", None)
			if pos_th is not None and vel_th is not None:
				val_payload["pos_th"] = (float(pos_th[0]), float(pos_th[1]))
				val_payload["vel_th"] = (float(vel_th[0]), float(vel_th[1]))
			if pos_sim is not None and vel_sim is not None:
				val_payload["pos_sim"] = (float(pos_sim[0]), float(pos_sim[1]))
				val_payload["vel_sim"] = (float(vel_sim[0]), float(vel_sim[1]))
			sim_state["validation"] = val_payload
		if getattr(config, "PROFILE_OVERLAY_ENABLED", False):
			tot_ms = (time.perf_counter() - frame_t0) * 1000.0
			sim_state["profile"] = {
				"physics_ms": float(physics_ms),
				"field_ms": float(field_ms),
				"draw_ms": float(draw_ms),
				"total_ms": float(tot_ms),
			}
		draw_overlay(screen, font, sim_state, input_state.overlay_enabled)
		render_hover_tooltip(screen, font, sim, input_state, ppm)

		pygame.display.flip()
		clock.tick(config.FPS_TARGET)


if __name__ == "__main__":
	try:
		main()
	except SystemExit:
		raise
	except Exception as exc:
		print(f"Error: {exc}", file=sys.stderr)
		raise
