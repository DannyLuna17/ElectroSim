# Annotated: electrosim.rendering.trails

## draw_trails
- Reuses a cached alpha surface per window size; clears each frame.
- For each particle history segment:
  - Skip if jump exceeds half window (wrap discontinuity guard).
  - Compute age-based fade; draw an outer edge line with reduced alpha for a simple AA effect, then the core line.
- Blit the trails surface onto the main screen.




