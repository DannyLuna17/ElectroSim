# Visualization

ElectroSim provides rich real-time visualization. This page describes the available visualization modes and customization options.

## Particle Rendering

### Color Coding

Particles are color-coded by charge:
- **Red**: Positive charge (q > 0)
- **Blue**: Negative charge (q < 0)
- **White**: Neutral (|q| < 10⁻¹² C, effectively zero)

Colors are defined in `electrosim/config.py`:
- `COLOR_POSITIVE`: RGB for positive particles (default: red)
- `COLOR_NEGATIVE`: RGB for negative particles (default: blue)
- `COLOR_NEUTRAL`: RGB for neutral particles (default: white)

### Particle Glow Effect

Particles can display a soft glow that scales with charge magnitude. Toggle with `B` key.

**Configuration** (`electrosim/config.py`):
- `GLOW_ENABLED`: Enable/disable glow (default: `True`)
- `GLOW_ALPHA_AT_MAX`: Alpha value when |q| = MAX_CHARGE_C (default: 255)
- `GLOW_RADIUS_SCALE`: Glow radius multiplier (default: 100.0)

The glow uses cached surfaces for performance. Cache settings:
- `GLOW_CACHE_INTENSITY_STEPS`: Quantization steps for intensity
- `GLOW_CACHE_MAX_SURFACES`: Maximum cached glow surfaces

### Particle Borders

- **White border**: Selected particle
- **Gold border**: Fixed (immobile) particle
- Both borders can appear simultaneously for a selected fixed particle

Border colors in config:
- `COLOR_SELECTED_BORDER`: Selection highlight (white)
- `COLOR_FIXED_BORDER`: Fixed particle indicator (gold)

## Electric Field Visualization

Press `E` to toggle electric field visualization. The field is sampled on a grid and rendered as vector arrows.

### Display Modes

Press `M` to cycle between two field visualization modes:

#### Brightness Mode

- **Arrow length**: Fixed (`FIELD_FIXED_ARROW_LENGTH_PX`, default: 16 px)
- **Arrow opacity/brightness**: Varies with field magnitude |E|
- **Color blending**: Arrows blend toward white at high field strength
- **Best for**: Showing field structure without clutter

Scaling parameter:
- `FIELD_BRIGHTNESS_SCALE`: Multiplier for brightness mapping (default: 2.0)

#### Length Mode

- **Arrow length**: Proportional to |E|, clamped to max
- **Arrow opacity**: Constant
- **Best for**: Direct magnitude comparison

Scaling parameters:
- `FIELD_VECTOR_SCALE`: Conversion from field strength to pixels (default: 2e-3)
- `FIELD_VECTOR_MAX_LENGTH_PX`: Maximum arrow length (default: 50.0 px)

### Field Grid Configuration

- `FIELD_GRID_STEP_PX`: Spacing between field sample points (default: 30 px)
  - Smaller values: Higher resolution, more computation
  - Larger values: Coarser grid, faster rendering
- `FIELD_ALPHA_MIN_DRAW`: Minimum alpha to draw (default: 2, suppresses very weak fields)

### Field Sampler

For performance with many particles, enable the field sampler:

- `FIELD_SAMPLER_ENABLED`: Cache field grid per frame (default: `True`)

When enabled, the entire field grid is computed once per frame and reused for rendering. Disable if you prefer on-demand field evaluation.

**Implementation**: {mod}`electrosim.rendering.field_sampler.ElectricFieldSampler`

## Force Vectors

Press `F` to show force vectors on each particle.

- **Color**: Yellow (configurable via `COLOR_FORCE_VECTOR`)
- **Length**: Proportional to force magnitude
- **Scaling**: `FORCE_VECTOR_SCALE` (default: 100.0 px per Newton)
- **Max length**: `VECTOR_MAX_LENGTH_PX` (default: 80.0 px)

Force vectors originate at the particle center and point in the direction of net electromagnetic force.

## Velocity Vectors

Press `V` to show velocity vectors on each particle.

- **Color**: Green (configurable via `COLOR_VELOCITY_VECTOR`)
- **Length**: Proportional to speed
- **Scaling**: `VELOCITY_VECTOR_SCALE` (default: 10.0 px per m/s)
- **Max length**: `VECTOR_MAX_LENGTH_PX` (default: 80.0 px)

Velocity vectors originate at the particle center and point in the direction of motion.

## Particle Trajectories

Press `T` to toggle trajectory trails.

### Trail Appearance

Trails are polylines that fade from recent to old positions:
- **Color**: 
  - Positive particles: `COLOR_TRAIL_POS` (light red)
  - Negative particles: `COLOR_TRAIL_NEG` (light blue)
- **Width**: `TRAIL_WIDTH_PX` (default: 3 px)
- **Alpha**: Fades from `TRAIL_ALPHA_MAX` to `TRAIL_MIN_ALPHA` over time
- **Duration**: `TRAJECTORY_HISTORY_SECONDS` (default: 3.0 s)

### Trail Configuration

Parameters in `electrosim/config.py`:
- `TRAIL_WIDTH_PX`: Line thickness
- `TRAIL_ALPHA_MAX`: Maximum opacity for newest trail segment (default: 235)
- `TRAIL_MIN_ALPHA`: Minimum opacity for oldest visible segment (default: 5)
- `TRAIL_FADE_SECONDS`: Fade duration (default: same as history duration)
- `TRAIL_AA_EDGE_EXTEND_PX`: Anti-aliasing edge width (default: 1 px)
- `TRAIL_AA_EDGE_OPACITY_FACTOR`: Edge opacity multiplier (default: 0.35)

Trails use a dedicated surface with alpha blending for smooth fading.

**Implementation**: {mod}`electrosim.rendering.trails`

## Metric Grid

Press `G` to toggle the metric grid overlay.

Shows world-space coordinates in meters:
- **Minor lines**: Every `GRID_METER_STEP` meters (default: 1.0 m)
- **Major lines**: Every `GRID_MAJOR_EVERY` steps (default: 1)
- **Colors**: 
  - Minor: `COLOR_GRID` (dark gray)
  - Major: `COLOR_GRID_MAJOR` (lighter gray)
- **Line widths**: 
  - Minor: `GRID_LINE_WIDTH` (default: 1 px)
  - Major: `GRID_MAJOR_LINE_WIDTH` (default: 2 px)

The grid helps visualize particle positions and distances in physical units.

## Overlay Information

The top-left overlay displays real-time statistics:

- **FPS**: Current frame rate
- **N**: Number of particles
- **Speed**: Simulation speed multiplier (0.5×, 1×, 2×, 4×)
- **dt**: Integration timestep (seconds)
- **Substeps**: RK4 substeps per frame
- **E_kin**: Total kinetic energy (Joules)
- **E_pot**: Total potential energy (Joules)
- **E_tot**: Total energy (Joules)

### Performance Profiling

Enable detailed per-frame timing with `PROFILE_OVERLAY_ENABLED = True`:

Additional overlay metrics:
- **Physics**: Time spent computing forces and integration (ms)
- **Field**: Time spent computing/rendering electric field (ms)
- **Render**: Time spent drawing particles, trails, vectors (ms)
- **Total**: Total frame time (ms)

**Overlay configuration**:
- `OVERLAY_TEXT_COLOR`: Text color (default: light gray)
- `OVERLAY_SHADOW_COLOR`: Shadow color (default: black)
- `OVERLAY_SHADOW_OFFSET`: Shadow offset in pixels (default: (1, 1))

**Implementation**: {mod}`electrosim.rendering.overlay`

## Background and Theme

Background color is configurable:
- `COLOR_BG`: Background RGB (default: dark gray, (18, 18, 22))

ElectroSim uses a dark theme by default for better contrast with bright particles and field vectors.

## Performance Considerations

Visualization can be the performance bottleneck for large numbers of particles:

1. **Electric field**: Most expensive, especially with many particles
   - Reduce `FIELD_GRID_STEP_PX` for fewer sample points
   - Enable `FIELD_SAMPLER_ENABLED` for caching
   - Use brightness mode instead of length mode

2. **Particle glow**: Moderate cost due to alpha blending
   - Disable with `GLOW_ENABLED = False` or press `B`
   - Reduce `GLOW_RADIUS_SCALE` for smaller glows

3. **Trajectories**: Moderate cost, scales with history length
   - Reduce `TRAJECTORY_HISTORY_SECONDS` for shorter trails
   - Disable with `T` key

4. **Vectors**: Low cost unless many particles
   - Disable force/velocity vectors (`F`, `V`) if not needed

## Related Documentation

- [Controls](controls.md) — Keyboard shortcuts for toggling visualizations
- [Configuration](configuration.md) — All visualization config parameters
- {mod}`electrosim.rendering.field` — Electric field rendering
- {mod}`electrosim.rendering.particles` — Particle rendering with glow
- {mod}`electrosim.rendering.trails` — Trajectory trail system
- {mod}`electrosim.rendering.overlay` — HUD and statistics display

