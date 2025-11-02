# Performance Notes

ElectroSim targets smooth real-time feedback while solving an $\mathcal{O}(N^2)$
pairwise problem. This page explains where CPU time goes, how to profile it, and
which configuration knobs provide the biggest wins.

## Built-in Profiling

The desktop build instruments the main loop in `main.py`:

- `physics_ms`: Time spent in {mod}`electrosim.simulation.engine.Simulation.step_frame`
  covering RK4 substeps, force evaluation, collision handling, and trajectory
  bookkeeping.
- `field_ms`: Time to rasterise the electric field grid inside
  {func}`electrosim.rendering.draw.draw_field_grid`.
- `draw_ms`: Remaining render cost (particles, glow, trails, vectors, overlays).
- `total_ms`: End-to-end frame duration.

Enable the overlay with `PROFILE_OVERLAY_ENABLED = True` in
`electrosim/config.py`. Toggle visibility during runtime with the `O` key.
Values are averaged per frame, so transient spikes are easy to spot.

For deeper inspection run ElectroSim under an external profiler (e.g. `py-spy`)
and filter for modules under `electrosim.simulation` and `electrosim.rendering`.

## Cost Drivers

### Physics

- Pairwise accelerations scale as $\mathcal{O}(N^2)$ per substep. Kernels live in
  {mod}`electrosim.simulation.physics` and are JIT-compiled with Numba when
  available.
- `NUMBA_PARALLEL_ACCEL = True` activates `prange` parallel loops, giving near
  linear speed-up on multi-core CPUs. Disable if you observe oversubscription or
  when debugging.
- `NUMBA_FASTMATH = True` permits aggressive floating-point simplifications.
  Use only when tiny energy drift is acceptable.
- Neutral, fixed, or massless particles are skipped to avoid unnecessary work.

### Field Grid

- Complexity is $\mathcal{O}(MN)$ where $M$ is the number of grid samples.
- `FIELD_GRID_STEP_PX` controls $M$. Doubling the spacing roughly quarters the
  cost at the expense of spatial resolution.
- With `FIELD_SAMPLER_ENABLED = True`, the grid is cache-computed once per frame
  (see {mod}`electrosim.rendering.field_sampler`). Disable for debugging to force
  per-pixel evaluation.
- In Pyodide builds Numba is unavailable; everything runs through the pure
  Python path, so consider coarser grids for browser deployments.

### Rendering

- **Glow**: Alpha blended surfaces cached inside
  {func}`electrosim.rendering.primitives.draw_glow_at_screen_pos`. The cache
  (`_GLOW_CACHE`) size is capped by `GLOW_CACHE_MAX_SURFACES`; lower it if
  memory is tight.
- **Trails**: {mod}`electrosim.rendering.trails` keeps a dedicated surface. Cost
  scales with sample frequency (`FPS_TARGET`) and history length
  (`TRAJECTORY_HISTORY_SECONDS`).
- **Vectors**: Force/velocity arrows are cheap individually but multiply by
  particle count. Clamp with `VECTOR_MAX_LENGTH_PX` to avoid overstretching that
  stresses the rasteriser.

## Tuning Workflow

1. **Characterise the baseline**: Start with a realistic particle count, enable
   the profiling overlay, and note `physics_ms`, `field_ms`, and `draw_ms`.
2. **Manage particle count**: Keep `MAX_PARTICLES` modest for interactive use.
   Consider scenario-specific limits if you build scripted demos.
3. **Balance timestep vs accuracy**: Lower `SUBSTEPS_BASE_PER_FRAME` or `FPS_TARGET`
   to trade precision for speed. Validation mode (`U` key) is helpful to make
   sure the integrator still behaves.
4. **Optimise the field**: Increase `FIELD_GRID_STEP_PX`, stick with brightness
   mode (fixed-length arrows), or disable the field entirely while debugging.
5. **Trim visuals**: Toggle glow (`B`), trails (`T`), force (`F`) and velocity (`V`)
   vectors as needed. If glow is required, try reducing `GLOW_RADIUS_SCALE` for
   smaller blended quads.

## Batch Experiments

The simulation orchestrator exposes all necessary hooks for scripted sweeps.
Use {class}`electrosim.simulation.engine.Simulation` from a Python shell or test
to:

```python
from electrosim.simulation.engine import Simulation

sim = Simulation()
sim.clear()
# populate custom scenario here
for _ in range(600):
    sim.step_frame()
print(sim.energy_tot)
```

Combine this with adjustments to `config` to benchmark multiple parameter sets
without rendering overhead. This is especially useful when validating new force
approximations or experimenting with alternative timestep controllers.

## Browser Considerations

The Pyodide build is typically 2–5× slower than the native desktop version:

- No Numba acceleration; only the pure Python kernels execute.
- WebGL canvas uploads add latency for each frame.
- Heavy trail histories and dense field grids quickly saturate the UI thread.

Keep `FIELD_GRID_STEP_PX` large (40–60), disable glow by default, and limit the
particle count to fewer than ~20 for smooth behaviour. These overrides are
captured in `web/config_web.py`.