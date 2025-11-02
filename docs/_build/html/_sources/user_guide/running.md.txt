# Running the Simulation

ElectroSim is an interactive 2D simulator of charged particles under Coulomb forces on a periodic domain.

## Basic Launch

To start the desktop version:

```bash
python main.py
```

The simulation window will open with a default scene containing one particle in the center.

## Window Configuration

Window size and display settings are configured in `electrosim/config.py`:

- `WINDOW_WIDTH_PX`: Window width in pixels (default: 1280)
- `WINDOW_HEIGHT_PX`: Window height in pixels (default: 800)
- `FPS_TARGET`: Target frame rate (default: 60)

Changes to these values require restarting the simulation.

## Time Integration

The simulation uses fixed timestep integration with configurable speed:

- **Base timestep**: `DT_S` (default: 0.001 s = 1 ms per substep)
- **Substeps per frame**: `SUBSTEPS_BASE_PER_FRAME` × speed multiplier
- **Speed multipliers**: 0.5×, 1×, 2×, 4× (controlled by keys 1-4)

For example, at 2× speed with 8 base substeps:
- Each frame advances by 8 × 2 = 16 substeps
- Physical time per frame: 16 × 0.001 s = 0.016 s
- At 60 FPS, simulation runs at approximately 60 × 0.016 = 0.96 s of physics per real second

## Default Scene

On startup, ElectroSim loads a default scene with:
- One negative particle at the center

You can modify this default scene in the `reset_to_default_scene()` method of the `Simulation` class.

## Performance Monitoring

The overlay (top-left corner) displays real-time statistics:
- **FPS**: Actual frame rate
- **N**: Number of particles
- **Speed**: Current speed multiplier (0.5×, 1×, 2×, or 4×)
- **dt**: Integration timestep
- **Substeps**: Number of RK4 steps per frame
- **E_kin, E_pot, E_tot**: Energy values

Enable detailed profiling with `PROFILE_OVERLAY_ENABLED = True` in config to see per-frame timing breakdown.

## Related Documentation

- [Controls](controls.md) — Keyboard and mouse inputs
- [Configuration](configuration.md) — All configuration options
- {mod}`electrosim.simulation.engine` — Simulation stepping pipeline
- {mod}`main` — Entry point and main loop

