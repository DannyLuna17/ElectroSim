# Annotated: electrosim.rendering.field_sampler

## ElectricFieldSampler
- Parameters: world size (m), pixels-per-meter, grid step (px), softening fraction.
- Buffers: `_centers_px`, `_vectors_px`, `_centers_m`.

## _grid_dims
- Converts world size and grid step to `(rows, cols)` with center at half-step.

## recompute
- Fills grid center coordinates in px and meters.
- Packs particles into SoA arrays for Numba kernel; computes `E` for all centers.
- Fallback path computes per cell via Python `electric_field_at_point`.
- Stores centers and vectors for drawing.

## iter_centers_and_vectors_px
- Yields tuples `((x,y), (Ex, Ey))` over the grid.




