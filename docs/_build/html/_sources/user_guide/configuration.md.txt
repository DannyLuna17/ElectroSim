# Configuration

All configuration for ElectroSim is centralized in `electrosim/config.py`. This file contains constants that control window size, physics parameters, visualization appearance, and performance optimizations.

**Important**: Changes to configuration require restarting the simulation to take effect.

## Window and Display

### Window Size

- `WINDOW_WIDTH_PX`: Window width in pixels (default: `1280`)
- `WINDOW_HEIGHT_PX`: Window height in pixels (default: `800`)
- `FPS_TARGET`: Target frame rate (default: `60`)

### World Scale

- `PIXELS_PER_METER`: Conversion factor (default: `80.0`, meaning 1 meter = 80 pixels)
- `WORLD_WIDTH_M`: Physical world width in meters (calculated: `WINDOW_WIDTH_PX / PIXELS_PER_METER` = 16.0 m)
- `WORLD_HEIGHT_M`: Physical world height in meters (calculated: `WINDOW_HEIGHT_PX / PIXELS_PER_METER` = 10.0 m)

The world is a periodic 2D torus: particles wrapping off one edge reappear on the opposite edge.

## Physics Parameters

### Fundamental Constants

- `K_COULOMB`: Coulomb's constant (N·m²/C², default: `8.9875517873681764e9`)

### Time Integration

- `DT_S`: Fixed timestep per substep in seconds (default: `0.001` s = 1 ms)
- `SUBSTEPS_BASE_PER_FRAME`: Base number of RK4 substeps per frame (default: `8`)
- `SPEED_MULTIPLIERS`: Available speed settings (default: `(0.5, 1.0, 2.0, 4.0)`)

At 1× speed with 8 substeps/frame and 60 FPS:
- Each frame advances 8 × 0.001 s = 0.008 s of simulation time
- Real-time factor: 60 × 0.008 = 0.48× (slower than real time)

### Softening

- `SOFTENING_FRACTION`: Plummer softening as fraction of contact radius (default: `0.1`)

Softening radius for pairwise forces: `ε = SOFTENING_FRACTION × (r_i + r_j)`

This prevents singularities when particles get very close. See [Mathematical Foundations](../math/plummer_softening.md) for details.

## Particle Defaults and Limits

### Default Properties

- `DEFAULT_CHARGE_C`: Default charge magnitude in Coulombs (default: `5e-6` C = 5 µC)
- `DEFAULT_MASS_KG`: Default particle mass in kg (default: `0.02` kg = 20 g)
- `DEFAULT_RADIUS_M`: Default particle radius in meters (default: `0.1` m = 10 cm)

### Allowed Ranges

- `MIN_CHARGE_C` / `MAX_CHARGE_C`: Charge range (default: `-100e-6` to `100e-6` C)
- `MIN_MASS_KG` / `MAX_MASS_KG`: Mass range (default: `0.005` to `0.2` kg)
- `MIN_RADIUS_M` / `MAX_RADIUS_M`: Radius range (default: `0.02` to `0.15` m)

### Limits

- `MAX_PARTICLES`: Maximum number of particles (default: `100`)

Exceeding this limit prevents adding more particles.

### Editing Step Sizes

When using keyboard shortcuts (Q/W for charge, A/S for mass, Z/X for radius):
- `CHARGE_STEP_C`: Charge increment (default: `1e-6` C = 1 µC)
- `MASS_STEP_KG`: Mass increment (default: `0.005` kg = 5 g)
- `RADIUS_STEP_M`: Radius increment (default: `0.005` m = 5 mm)

## Visualization Settings

### Colors

All colors are RGB tuples (0-255 range):

**Background and UI**:
- `COLOR_BG`: Background (default: `(18, 18, 22)`, dark gray)
- `COLOR_GRID`: Minor grid lines (default: `(35, 35, 40)`)
- `COLOR_GRID_MAJOR`: Major grid lines (default: `(60, 60, 70)`)

**Particles**:
- `COLOR_POSITIVE`: Positive charge (default: `(255, 85, 85)`, red)
- `COLOR_NEGATIVE`: Negative charge (default: `(75, 139, 255)`, blue)
- `COLOR_NEUTRAL`: Neutral particles (default: `(255, 255, 255)`, white)
- `COLOR_FIXED_BORDER`: Fixed particle border (default: `(230, 200, 80)`, gold)
- `COLOR_SELECTED_BORDER`: Selected particle border (default: `(255, 255, 255)`, white)

**Vectors and Fields**:
- `COLOR_FORCE_VECTOR`: Force arrows (default: `(255, 225, 100)`, yellow)
- `COLOR_VELOCITY_VECTOR`: Velocity arrows (default: `(120, 255, 120)`, green)
- `COLOR_FIELD_VECTOR`: Electric field arrows (default: `(30, 200, 60)`, green)

**Trails**:
- `COLOR_TRAIL_POS`: Positive particle trails (default: `(255, 120, 120)`, light red)
- `COLOR_TRAIL_NEG`: Negative particle trails (default: `(120, 160, 255)`, light blue)

### Electric Field

- `FIELD_VIS_MODE`: Display mode, either `"brightness"` or `"length"` (default: `"brightness"`)
- `FIELD_GRID_STEP_PX`: Spacing between field sample points in pixels (default: `30`)
- `FIELD_VECTOR_MAX_LENGTH_PX`: Maximum arrow length (default: `50.0`)
- `FIELD_VECTOR_SCALE`: Scaling from field strength to pixels (default: `2e-3`)
- `FIELD_FIXED_ARROW_LENGTH_PX`: Fixed arrow length in brightness mode (default: `16.0`)
- `FIELD_BRIGHTNESS_SCALE`: Brightness mode intensity multiplier (default: `2.0`)
- `FIELD_ALPHA_MIN_DRAW`: Minimum alpha to render (default: `2`, suppresses very weak fields)

### Glow Effect

- `GLOW_ENABLED`: Enable particle glow (default: `True`)
- `GLOW_ALPHA_AT_MAX`: Alpha when |q| = MAX_CHARGE_C (default: `255`)
- `GLOW_RADIUS_SCALE`: Glow size multiplier (default: `100.0`)
- `GLOW_CACHE_INTENSITY_STEPS`: Cache quantization (default: `1`)
- `GLOW_CACHE_MAX_SURFACES`: Maximum cached surfaces (default: `12000000`)

### Trails

- `TRAJECTORY_HISTORY_SECONDS`: Trail duration (default: `3.0` s)
- `TRAIL_WIDTH_PX`: Trail line width (default: `3`)
- `TRAIL_ALPHA_MAX`: Maximum trail opacity (default: `235`)
- `TRAIL_MIN_ALPHA`: Minimum trail opacity (default: `5`)
- `TRAIL_FADE_SECONDS`: Fade duration (default: `3.0` s)
- `TRAIL_AA_EDGE_EXTEND_PX`: Anti-aliasing edge width (default: `1`)
- `TRAIL_AA_EDGE_OPACITY_FACTOR`: Edge opacity factor (default: `0.35`)

### Vectors

- `FORCE_VECTOR_SCALE`: Pixels per Newton (default: `100.0`)
- `VELOCITY_VECTOR_SCALE`: Pixels per m/s (default: `10.0`)
- `VECTOR_MAX_LENGTH_PX`: Maximum vector length (default: `80.0`)

### Metric Grid

- `GRID_METER_STEP`: Spacing between grid lines in meters (default: `1.0`)
- `GRID_MAJOR_EVERY`: Major line frequency (default: `1`, every line is major)
- `GRID_LINE_WIDTH`: Minor line width (default: `1`)
- `GRID_MAJOR_LINE_WIDTH`: Major line width (default: `2`)

### Overlay

- `OVERLAY_TEXT_COLOR`: Text color (default: `(230, 230, 230)`, light gray)
- `OVERLAY_SHADOW_COLOR`: Shadow color (default: `(0, 0, 0)`, black)
- `OVERLAY_SHADOW_OFFSET`: Shadow offset (default: `(1, 1)`)

## Performance Options

### Field Computation

- `FIELD_SAMPLER_ENABLED`: Cache field grid per frame (default: `True`)

When enabled, the electric field grid is computed once per frame and reused. Disable for on-demand computation.

### Numba Acceleration

- `NUMBA_PARALLEL_ACCEL`: Use parallel loops in Numba kernels (default: `True`)
- `NUMBA_FASTMATH`: Allow fast math approximations (default: `False`)

**Notes**:
- Parallel acceleration uses multiple CPU cores for force computation
- Fast math trades slight accuracy for performance
- If Numba is unavailable, simulation falls back to pure NumPy automatically

### Profiling

- `PROFILE_OVERLAY_ENABLED`: Show per-frame timing breakdown (default: `True`)

Displays physics, field, and rendering times in the overlay.

## Interaction Settings

### Mouse Input

- `VELOCITY_PER_PIXEL`: Initial velocity per pixel dragged (default: `0.2` m/s per pixel)
- `VELOCITY_MAX_MPS`: Maximum initial velocity (default: `10.0` m/s)

When placing a particle by dragging, the drag distance sets the initial velocity.

### Charge Threshold

- `NEUTRAL_CHARGE_EPS`: Threshold for neutral particle detection (default: `1e-12` C)

Particles with |q| < `NEUTRAL_CHARGE_EPS` are rendered as neutral (white) to avoid color flicker from floating-point rounding.

## Validation Settings

These parameters control the built-in uniform field validation scenario:

- `UNIFORM_FIELD_ACTIVE`: Enable uniform field contribution (default: `False`)
- `UNIFORM_FIELD_VECTOR_NC`: Constant field vector in N/C (default: `(500.0, 0.0)`)
- `UNIFORM_FIELD_VISUAL_OVERRIDE`: Show only uniform field (default: `False`)
- `VALIDATION_DURATION_S`: Validation scenario duration (default: `10.0` s)
- `COLOR_THEORY_TRAJECTORY`: Theoretical trajectory color (default: `(230, 230, 80)`, yellow)

See [Validation](../developer_guide/validation.md) for details on using these features.

## Configuration Workflow

1. **Edit** `electrosim/config.py` with desired changes
2. **Save** the file
3. **Restart** the simulation (`python main.py`)
4. **Verify** changes took effect

For rapid iteration on visualization parameters, consider exposing them as runtime toggles in the UI (requires code modification).

## Web Version Overrides

The web version uses `web/config_web.py` to override certain desktop defaults for browser compatibility:

- Lower FPS target for browser performance
- Adjusted field sampler settings
- Different profiling defaults

See [Web Integration](../developer_guide/web_integration.md) for details.

## Performance Tuning Guide

For best performance with many particles:

1. **Disable expensive features**:
   - Set `GLOW_ENABLED = False`
   - Increase `FIELD_GRID_STEP_PX` (e.g., 40-50)
   - Reduce `TRAJECTORY_HISTORY_SECONDS` (e.g., 1.0-2.0)

2. **Enable optimizations**:
   - Set `FIELD_SAMPLER_ENABLED = True`
   - Set `NUMBA_PARALLEL_ACCEL = True`
   - Consider `NUMBA_FASTMATH = True` (slight accuracy loss)

3. **Reduce time resolution**:
   - Decrease `SUBSTEPS_BASE_PER_FRAME` (e.g., 4-6)
   - Lower `FPS_TARGET` (e.g., 30-45)

4. **Limit particle count**:
   - Keep `MAX_PARTICLES` modest (< 50 for smooth real-time)

See [Performance Notes](../developer_guide/performance.md) for detailed analysis.

## Related Documentation

- [Visualization](visualization.md) — How visualization settings affect rendering
- [Running](running.md) — How configuration affects simulation behavior
- [Performance](../developer_guide/performance.md) — Performance optimization strategies
- {mod}`electrosim.config` — API reference for all config constants

