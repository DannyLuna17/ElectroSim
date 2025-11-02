# Annotated: electrosim.rendering.field

## _get_sampler
- Constructs a cache key from `(world_size, ppm, grid_step_px, softening_fraction)` to reuse samplers.

## draw_field_grid
- Computes screen width/height in pixels.
- Brightness mode:
  - Recompute sampler; draw onto an alpha surface; per-arrow alpha/color from |E|; fixed arrow length.
  - Single blit of the composed surface for performance.
- Sampler length mode:
  - Reuse sampler; per-arrow length scales with |E| clamped to `FIELD_VECTOR_MAX_LENGTH_PX*0.6`.
- Direct mode (no sampler):
  - Iterate grid points; call `electric_field_at_point` per cell; map to pixels.

Related: {mod}`electrosim.rendering.field_sampler`, {py:func}`electrosim.simulation.physics.electric_field_at_point`.




