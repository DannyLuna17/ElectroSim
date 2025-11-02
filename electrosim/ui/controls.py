from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame
import numpy as np

from electrosim import config
from electrosim.simulation.engine import Simulation
from electrosim.rendering.draw import screen_vector_to_world, draw_glow_at_screen_pos
from electrosim.simulation.physics import electric_field_at_point, minimum_image_displacement


@dataclass
class InputState:
    """UI state for placement, dragging and tooltips across frames.
 
    Attributes
    ----------
    placing : bool
        Whether a placement gesture is in progress.
    place_start_px, place_current_px : tuple[int,int]
        Drag start and current pixels during placement.
    placing_negative : bool
        If True, next placed particle is negative.
    placing_fixed : bool
        If True, next placed particle starts fixed.
    tooltip_enabled : bool
        Show or hide hover tooltip.
    overlay_enabled : bool
        Show or hide information overlay.
    mouse_pos_px : tuple[int,int]
        Last mouse position.
    dragging_selected : bool
        Whether a drag of the selected particle is active.
    drag_prev_fixed : bool
        Stored fixed state before drag (restored on release).
    drag_prev_velocity_mps : tuple[float,float] | None
        Stored velocity before drag (restored on release).
    """
    placing: bool = False
    place_start_px: Tuple[int, int] = (0, 0)
    place_current_px: Tuple[int, int] = (0, 0)
    placing_negative: bool = False
    placing_fixed: bool = False
    tooltip_enabled: bool = True
    overlay_enabled: bool = True
    mouse_pos_px: Tuple[int, int] = (0, 0)
    dragging_selected: bool = False
    drag_prev_fixed: bool = False
    drag_prev_velocity_mps: Tuple[float, float] | None = None


def handle_events(pg: pygame, sim: Simulation, input_state: InputState, pixels_per_meter: float) -> None:
    """Process pygame events to drive simulation state and UI interactions.

    Parameters
    ----------
    pg : pygame module
        Pygame module for quitting.
    sim : Simulation
        Simulation instance to manipulate.
    input_state : InputState
        Mutable UI state across frames.
    pixels_per_meter : float
        Pixels-per-meter scale.
    """
    def _clamp_to_window(px: int, py: int) -> Tuple[int, int]:
        win_w = config.WINDOW_WIDTH_PX
        win_h = config.WINDOW_HEIGHT_PX
        return max(0, min(px, win_w - 1)), max(0, min(py, win_h - 1))

    def _begin_drag_selected(mx: int, my: int) -> None:
        # Begin dragging selected particle
        input_state.dragging_selected = True
        p = sim.particles[sim.selected_index]
        input_state.drag_prev_fixed = p.fixed
        input_state.drag_prev_velocity_mps = (float(p.vel_mps[0]), float(p.vel_mps[1]))
        p.fixed = True
        cx, cy = _clamp_to_window(mx, my)
        p.pos_m = screen_vector_to_world((cx, cy), pixels_per_meter)

    def _update_drag(mx: int, my: int) -> None:
        if sim.selected_index is None or sim.selected_index < 0 or sim.selected_index >= len(sim.particles):
            input_state.dragging_selected = False
            return
        cx, cy = _clamp_to_window(mx, my)
        p = sim.particles[sim.selected_index]
        p.fixed = True
        p.pos_m = screen_vector_to_world((cx, cy), pixels_per_meter)

    def _end_drag() -> None:
        if sim.selected_index is not None and 0 <= sim.selected_index < len(sim.particles):
            p = sim.particles[sim.selected_index]
            p.fixed = input_state.drag_prev_fixed
            if input_state.drag_prev_velocity_mps is not None:
                p.vel_mps[0] = input_state.drag_prev_velocity_mps[0]
                p.vel_mps[1] = input_state.drag_prev_velocity_mps[1]
        input_state.dragging_selected = False
        input_state.drag_prev_velocity_mps = None

    def _begin_placement(mx: int, my: int) -> None:
        input_state.placing = True
        input_state.place_start_px = (mx, my)
        input_state.place_current_px = (mx, my)
        mods = pygame.key.get_mods()
        input_state.placing_negative = (mods & pygame.KMOD_SHIFT) != 0
        input_state.placing_fixed = (mods & pygame.KMOD_ALT) != 0 or (mods & pygame.KMOD_CTRL) != 0

    def _commit_placement() -> None:
        start = input_state.place_start_px
        end = input_state.place_current_px
        pos_m = screen_vector_to_world(start, pixels_per_meter)
        drag_vec_px = (end[0] - start[0], end[1] - start[1])
        vel = np.array([
            float(drag_vec_px[0]) * config.VELOCITY_PER_PIXEL,
            float(drag_vec_px[1]) * config.VELOCITY_PER_PIXEL,
        ], dtype=float)
        speed = float(np.hypot(vel[0], vel[1]))
        if speed > config.VELOCITY_MAX_MPS:
            vel *= (config.VELOCITY_MAX_MPS / speed)
        charge = -config.DEFAULT_CHARGE_C if input_state.placing_negative else config.DEFAULT_CHARGE_C
        sim.add_particle(
            pos_m=pos_m,
            vel_mps=vel,
            charge_c=charge,
            mass_kg=config.DEFAULT_MASS_KG,
            radius_m=config.DEFAULT_RADIUS_M,
            fixed=input_state.placing_fixed,
        )
        input_state.placing = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pg.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                sim.paused = not sim.paused
            elif event.key == pygame.K_r:
                sim.reset_to_default_scene()
            elif event.key == pygame.K_ESCAPE:
                pg.quit()
                raise SystemExit
            elif event.key == pygame.K_c:
                sim.clear()
            elif event.key == pygame.K_f:
                sim.show_forces = not sim.show_forces
            elif event.key == pygame.K_v:
                sim.show_velocities = not sim.show_velocities
            elif event.key == pygame.K_e:
                sim.show_field = not sim.show_field
            elif event.key == pygame.K_m:
                config.FIELD_VIS_MODE = "length" if config.FIELD_VIS_MODE == "brightness" else "brightness"
            elif event.key == pygame.K_t:
                sim.show_trails = not sim.show_trails
            elif event.key == pygame.K_g:
                sim.show_meter_grid = not sim.show_meter_grid
            elif event.key == pygame.K_b:
                config.GLOW_ENABLED = not config.GLOW_ENABLED
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                sim.speed_index = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}[event.key]
            elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                sim.remove_selected_particle()
            elif event.key == pygame.K_SPACE:
                sim.toggle_selected_fixed()
            elif event.key == pygame.K_q:
                sim.adjust_selected_charge(-config.CHARGE_STEP_C)
            elif event.key == pygame.K_w:
                sim.adjust_selected_charge(+config.CHARGE_STEP_C)
            elif event.key == pygame.K_a:
                sim.adjust_selected_mass(-config.MASS_STEP_KG)
            elif event.key == pygame.K_s:
                sim.adjust_selected_mass(+config.MASS_STEP_KG)
            elif event.key == pygame.K_z:
                sim.adjust_selected_radius(-config.RADIUS_STEP_M)
            elif event.key == pygame.K_x:
                sim.adjust_selected_radius(+config.RADIUS_STEP_M)
            elif event.key == pygame.K_i:
                input_state.tooltip_enabled = not input_state.tooltip_enabled
            elif event.key == pygame.K_o:
                input_state.overlay_enabled = not input_state.overlay_enabled
            elif event.key == pygame.K_u:
                sim.start_uniform_field_validation()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            sim.select_particle_at_screen_pos(mx, my)
            if sim.selected_index is not None:
                _begin_drag_selected(mx, my)
            else:
                _begin_placement(mx, my)

        if event.type == pygame.MOUSEMOTION:
            input_state.mouse_pos_px = event.pos
            if input_state.placing:
                input_state.place_current_px = event.pos
            if input_state.dragging_selected:
                mx, my = event.pos
                _update_drag(mx, my)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if input_state.dragging_selected:
                _end_drag()
            elif input_state.placing:
                _commit_placement()


def render_placement_preview(screen: pygame.Surface, input_state: InputState, pixels_per_meter: float) -> None:
    """Render a live preview for particle placement with initial velocity.

    Parameters
    ----------
    screen : pygame.Surface
        Target surface.
    input_state : InputState
        Current UI placement state.
    pixels_per_meter : float
        Pixels-per-meter scale.
    """
    if not input_state.placing:
        return
    start = input_state.place_start_px
    current = input_state.place_current_px
    color = config.COLOR_NEGATIVE if input_state.placing_negative else config.COLOR_POSITIVE
    if config.GLOW_ENABLED:
        base_radius_px = max(2, int(round(config.DEFAULT_RADIUS_M * pixels_per_meter)))
        t = min(1, max(0.0, float(abs(config.DEFAULT_CHARGE_C) / config.MAX_CHARGE_C)))
        draw_glow_at_screen_pos(screen, start, base_radius_px-5, color, t)
    pygame.draw.circle(screen, color, start, max(2, int(round(config.DEFAULT_RADIUS_M * pixels_per_meter))), 1)
    pygame.draw.line(screen, color, start, current, 1)
    pygame.draw.circle(screen, color, current, 2)


def render_hover_tooltip(
    screen: pygame.Surface,
    font: pygame.font.Font,
    sim: Simulation,
    input_state: InputState,
    pixels_per_meter: float,
) -> None:
    """Render an informational tooltip with local E-field and nearest particle.

    Parameters
    ----------
    screen : pygame.Surface
        Target surface.
    font : pygame.font.Font
        Font used for text rendering.
    sim : Simulation
        Simulation to query.
    input_state : InputState
        Current UI state (mouse position and toggles).
    pixels_per_meter : float
        Pixels-per-meter scale.
    """
    
    # Visibility conditions
    if not input_state.tooltip_enabled:
        return
    if input_state.placing:
        return

    mx, my = input_state.mouse_pos_px

    # Compute world position and electric field at cursor
    pos_m = screen_vector_to_world((mx, my), pixels_per_meter)
    E = electric_field_at_point(pos_m, sim.particles, sim.world_size_m, config.SOFTENING_FRACTION)
    Emag = float(np.hypot(E[0], E[1]))

    # Find nearest particle
    nearest_idx = None
    nearest_dist_m = float("inf")
    for idx, p in enumerate(sim.particles):
        min_displacement = minimum_image_displacement(pos_m, p.pos_m, sim.world_size_m)
        dist = float(np.hypot(min_displacement[0], min_displacement[1]))
        if dist < nearest_dist_m:
            nearest_dist_m = dist
            nearest_idx = idx

    lines: list[str] = []
    lines.append(f"pos_x: ({int(mx)}, {int(my)})")
    lines.append(f"pos_m:  ({pos_m[0]:.3f}, {pos_m[1]:.3f})")
    lines.append(f"E:  ({E[0]:.3e}, {E[1]:.3e}) N/C")
    lines.append(f"|E|: {Emag:.3e} N/C")

    if nearest_idx is not None:
        p = sim.particles[nearest_idx]
        sel = " [selected]" if (sim.selected_index is not None and nearest_idx == sim.selected_index) else ""
        q_micro = p.charge_c * 1e6
        lines.append(
            (
                f"Nearest: id={p.id}{sel}, d={nearest_dist_m:.3f} m, q={q_micro:.3f} µC, "
            )
        )
        lines.append(
            (
                f"m={p.mass_kg:.3f} kg, r={p.radius_m:.3f} m, fixed={p.fixed}"
            )
        )
    else:
        lines.append("Nearest: none")

    # Render with background box near cursor, clamped to window
    padding_x = 8
    padding_y = 6
    line_spacing = 2

    renders = [font.render(text, True, config.OVERLAY_TEXT_COLOR) for text in lines]
    widths = [r.get_width() for r in renders]
    heights = [r.get_height() for r in renders]
    box_w = max(widths) + padding_x * 2
    box_h = sum(heights) + padding_y * 2 + line_spacing * (len(renders) - 1)

    # Preferred anchor bottom-right of cursor
    x = mx + 25
    y = my + 8

    # Clamp to window
    win_w = config.WINDOW_WIDTH_PX
    win_h = config.WINDOW_HEIGHT_PX
    if x + box_w > win_w:
        x = mx - 12 - box_w
    if y + box_h > win_h:
        y = my - 16 - box_h
    x = max(0, min(x, win_w - box_w))
    y = max(0, min(y, win_h - box_h))

    bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 50))
    screen.blit(bg, (x, y))

    # 1px border using shadow color
    pygame.draw.rect(screen, config.OVERLAY_SHADOW_COLOR, (x, y, box_w, box_h), 1)

    # Blit text lines
    ty = y + padding_y
    for r in renders:
        screen.blit(r, (x + padding_x, ty))
        ty += r.get_height() + line_spacing

    # Crosshair at cursor
    ch_len = 10
    col = config.OVERLAY_TEXT_COLOR
    pygame.draw.line(screen, col, (mx - ch_len, my), (mx + ch_len, my), 1)
    pygame.draw.line(screen, col, (mx, my - ch_len), (mx, my + ch_len), 1)
