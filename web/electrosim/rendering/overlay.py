from __future__ import annotations

import pygame

from electrosim import config


def draw_overlay(screen: pygame.Surface, font: pygame.font.Font, sim_state: dict, overlay_enabled: bool = True) -> None:
	"""Render a multi-line overlay with FPS, counts, energies, and controls.
 
	Parameters
	----------
	screen : pygame.Surface
		Target surface.
	font : pygame.font.Font
		Font used for text rendering.
	sim_state : dict
		Simulation state values including fps, n, speed_label, dt_s, substeps, energies,
		and optional profiling timings under key `profile`.
	overlay_enabled : bool
		Whether to render the overlay. If False, nothing is drawn.
	"""
	credits_text = "Created by Danny Luna | dannyq@uninorte.edu.co"
	credits_render = font.render(credits_text, True, config.OVERLAY_TEXT_COLOR)
	credits_shadow = font.render(credits_text, True, config.OVERLAY_SHADOW_COLOR)
	screen_width = screen.get_width()
	credits_x = screen_width - credits_render.get_width() - 10
	credits_y = 45
	screen.blit(credits_shadow, (credits_x + config.OVERLAY_SHADOW_OFFSET[0], credits_y + config.OVERLAY_SHADOW_OFFSET[1]))
	screen.blit(credits_render, (credits_x, credits_y))

	if not overlay_enabled:
		return
	
	lines = []
	lines.append(f"FPS: {sim_state['fps']:.1f}")
	lines.append(f"Particles: {sim_state['n']}")
	lines.append(f"Speed: {sim_state['speed_label']}")
	lines.append(f"dt: {sim_state['dt_s']:.4f} s  substeps/frame: {sim_state['substeps']}")
	lines.append(f"E_kin: {sim_state['E_kin']:.3e} J  E_pot_elec: {sim_state['E_pot']:.3e} J  E_tot: {sim_state['E_tot']:.3e} J")
	if getattr(config, "PROFILE_OVERLAY_ENABLED", False):
		prof = sim_state.get("profile")
		if prof:
			lines.append(
				f"performance (ms): physics={prof.get('physics_ms',0):.1f} field={prof.get('field_ms',0):.1f} draw={prof.get('draw_ms',0):.1f} total={prof.get('total_ms',0):.1f}"
			)
	lines.append("Controls: LMB=place, Shift=negative, Alt/Ctrl=fixed, P=pause, R=reset, C=clear, Esc=exit")
	lines.append("Editing: click=select, drag selected=move; Q/W charge, A/S mass, Z/X radius, Space=fixed, Delete=remove")
	lines.append("Show/Hide: G grid (meters), F forces, V velocities, E electric field, T trajectories, O overlay, I info tooltip, 1..4 speed")
	mode_label = "Fixed brightness" if config.FIELD_VIS_MODE == "brightness" else "Variable length"
	lines.append(f"Electric field (M): mode = {mode_label}")
	lines.append(f"Particle glow: B Show/Hide (state: {'ON' if config.GLOW_ENABLED else 'OFF'})")
	lines.append("Validation: U = uniform electric field (10 s)")

	# Validation summary
	val = sim_state.get("validation")
	if val and val.get("active"):
		E = val.get("E", (0.0, 0.0))
		a = val.get("a", (0.0, 0.0))
		t = float(val.get("t", 0.0))
		dt = float(val.get("dt_s", 0.0))
		pos_err = float(val.get("pos_err", 0.0))
		vel_err = float(val.get("vel_err", 0.0))
		lines.append(f"Validation: E=({E[0]:.2f},{E[1]:.2f}) N/C  a=({a[0]:.2f},{a[1]:.2f}) m/s^2")
		lines.append(f"t={t:.2f} s  dt={dt:.4f} s  |pos_err|={pos_err:.3e}  |vel_err|={vel_err:.3e}")
		# Final comparison if available
		if val.get("reached_end"):
			pth = val.get("pos_th")
			vth = val.get("vel_th")
			ps = val.get("pos_sim")
			vs = val.get("vel_sim")
			if pth and vth:
				lines.append(f"FINAL pos_th=({pth[0]:.3f},{pth[1]:.3f})  vel_th=({vth[0]:.3f},{vth[1]:.3f})")
			if ps and vs:
				lines.append(f"FINAL pos_sim=({ps[0]:.3f},{ps[1]:.3f})  vel_sim=({vs[0]:.3f},{vs[1]:.3f})")

	y = 45
	for text in lines:
		render = font.render(text, True, config.OVERLAY_TEXT_COLOR)
		shadow = font.render(text, True, config.OVERLAY_SHADOW_COLOR)
		screen.blit(shadow, (10 + config.OVERLAY_SHADOW_OFFSET[0], y + config.OVERLAY_SHADOW_OFFSET[1]))
		screen.blit(render, (10, y))
		y += render.get_height() + 2


