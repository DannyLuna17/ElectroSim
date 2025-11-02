# Annotated: electrosim.rendering.primitives

## world_vector_to_screen / screen_vector_to_world
- Linear conversion between meters and pixels using `PIXELS_PER_METER`.

## _draw_arrow
- Clamps vector length to `max_len_pixel` to avoid overlong arrows.
- Draws line, then arrow head using simple trig with head angle and length.

## draw_meter_grid
- Computes pixel width/height from world size and `PIXELS_PER_METER`.
- Draws vertical and horizontal lines at 1 m spacing (`GRID_METER_STEP`).
- Major lines every `GRID_MAJOR_EVERY`; thickness and color differ.
- The `+ 1e-9` in while conditions prevents missing the last line due to float rounding.

## draw_glow_at_screen_pos
- Early returns if disabled or zero intensity.
- Cache key includes size, color, quantized intensity, base radius.
- Generates radial falloff with cubic profile; fills RGB and alpha planes via `pygame.surfarray`.
- Bound cache size via `GLOW_CACHE_MAX_SURFACES`.
- Blit with additive blending to accumulate glow contributions.




