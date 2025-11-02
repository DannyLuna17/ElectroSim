# Annotated: electrosim.ui.controls

## InputState
- Tracks placement, dragging, tooltip toggle, and mouse position across frames.

## handle_events
- Keyboard:
  - Toggles pause, reset, quit, clear, display flags, speed, glow, selection edits.
- Mouse:
  - Left-down: select and begin drag if hit; else begin placement.
  - Motion: update placement preview and dragged particle position.
  - Left-up: end drag or commit placement (position and initial velocity derived from drag vector scaled by `VELOCITY_PER_PIXEL` and clamped by `VELOCITY_MAX_MPS`).
- Placement sets sign from Shift and fixed state from Alt/Ctrl.

## render_placement_preview
- Draws circle at start, line to current, small circle at end; optional glow.

## render_hover_tooltip
- Computes world position and local `E` under cursor.
- Finds nearest particle by minimum-image distance.
- Renders a clamped tooltip box with position, field, and nearest particle properties.




