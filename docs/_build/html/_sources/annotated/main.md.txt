# Annotated: main.py

## main
- Initializes Pygame, creates window, clock, and font.
- Instantiates `Simulation` and `InputState`.
- Frame loop:
  - Capture `frame_t0` for profiling.
  - Events: `handle_events` updates simulation state and toggles.
  - Physics timing around `sim.step_frame()`; compute `physics_ms`.
  - Drawing:
    - Clear background; optional meter grid and field grid (timed separately).
    - Draw glow, trails, particles, velocity/force vectors.
    - Placement preview and hover tooltip.
  - Compute and display overlay with FPS, energies, and timings.
  - Flip buffers and tick at target FPS.




