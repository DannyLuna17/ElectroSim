# Annotated: electrosim.simulation.engine

## Particle dataclass

- Fields: `id`, `pos_m (m)`, `vel_mps (m/s)`, `mass_kg (kg)`, `charge_c (C)`, `radius_m (m)`, `fixed (bool)`, `color_rgb`, `history` (deque of `(t, (x,y))`).
- Invariants: `id` re-assigned after deletions; `history` capped at 50k samples.

## Simulation.__init__
- Initializes world size from config; visualization toggles; speeds; energies; time.
- Calls `reset_to_default_scene()`; optionally warms Numba with a dummy accelerations call.

## reset_to_default_scene
- Clears state; adds a single particle at world center with default properties.
- Recomputes energies.

## clear
- Clears particles and resets timers, energies, selection, and last forces.

## add_particle
- Clamps input properties to config ranges.
- Assigns color by charge sign with `NEUTRAL_CHARGE_EPS` threshold.
- Appends to list and assigns `id = len(particles)-1`.

## _update_color
- Updates color on charge edits; neutral threshold prevents flicker.

## select_particle_at_screen_pos
- Converts pixel to world; computes minimum-image distance to each particle; selects nearest within a pixel radius threshold.

## adjust_selected_charge/mass/radius
- Clamps to config ranges and updates color when charge changes.

## toggle_selected_fixed
- Inverts `fixed` on selected if any.

## remove_selected_particle
- Deletes selected; reassigns contiguous ids; clears selection.

## recompute_energies
- Computes kinetic, potential, total using physics helpers.

## _wrap_all_positions
- Applies in-place modulo wrapping to every particle.

## _ensure_selected_valid
- Clears selection if the index is out of bounds after deletions.

## _compute_last_forces
- Computes accelerations and multiplies by mass for non-fixed particles; stores per-particle forces for drawing.

## update_trails / _advance_time_and_trails
- Advances `t_sim` and appends positions at a fixed sampling interval; prunes history older than `TRAJECTORY_HISTORY_SECONDS`.

## step_substep
- Early exit if paused.
- RK4 integrate positions/velocities; wrap; resolve collisions; wrap; validate selection.

## step_frame
- Early exit if paused.
- Compute substeps from `SUBSTEPS_BASE_PER_FRAME` and speed multiplier; loop substeps and accumulate simulation time.
- Once per frame: update trails, energies, and optionally last forces.




