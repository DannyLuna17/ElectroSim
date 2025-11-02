# Architecture

This page describes the high-level architecture of ElectroSim: modules, responsibilities, data flow, and key implementation details.

## Overview

ElectroSim follows a modular architecture separating concerns into:
- **Configuration**: Centralized constants
- **Simulation**: Physics state and time stepping
- **Rendering**: Visualization of particles, fields, and UI
- **Controls**: User input handling
- **Main Loop**: Integration of all subsystems

## Modules and responsibilities

### `electrosim.config`
Global configuration constants for all subsystems:
- **Window settings**: Resolution, FPS target, pixels-per-meter conversion
- **Physics parameters**: Coulomb constant, timestep, softening, particle limits
- **Visualization options**: Colors, field modes, glow settings, trail configuration
- **Performance flags**: Numba acceleration, field sampler caching, profiling

**Key features**:
- Single source of truth for all tunable parameters
- Type-annotated constants for IDE support
- Imported by all modules; changes require restart

### `electrosim.simulation.engine`
Core simulation state management and orchestration:

**`Particle` dataclass**:
- Fields: `pos_m` (position), `vel_mps` (velocity), `charge_c`, `mass_kg`, `radius_m`, `fixed` (boolean)
- Additional: `id`, `color`, `merge_history` for tracking combined particles
- Uses NumPy arrays for positions/velocities (vectorization-ready)

**`Simulation` class**:
- **State**: List of `Particle` objects, simulation time `t_sim`, speed multiplier
- **Methods**:
  - `step_frame()`: Advance simulation by one frame (multiple substeps)
  - `add_particle()`: Create new particle with validation
  - `remove_particle()`: Delete by index
  - `reset_to_default_scene()`: Load initial configuration
  - Validation mode: `start_validation_uniform_field()`, `end_validation()`
- **Responsibilities**:
  - Delegate physics to `physics` module
  - Manage particle lifecycle (creation, deletion, merging)
  - Track trails and energy history
  - Coordinate validation scenarios

### `electrosim.simulation.physics`
Physics kernels and numerical methods:

**Force computation**:
- `minimum_image_displacement()`: Periodic boundary wraparound
- `electric_force_pair()`: Coulomb force with softening between two particles
- `compute_accelerations()`: N² loop over all particle pairs
  - Numba JIT-compiled variants: serial and parallel (`prange`)
  - Fallback: Pure NumPy/Python when Numba unavailable
  - Skips: Fixed, massless, and neutral particles
  - Returns acceleration array for integration

**Time integration**:
- `rk4_integrate()`: Fourth-order Runge-Kutta stepper
  - Four-stage method: k1, k2, k3, k4
  - Temporary state management for intermediate evaluations
  - Writes back only to non-fixed particles
  - Respects periodic boundaries at each stage

**Collision handling**:
- `resolve_collisions()`: Two-pass collision resolution
  - **Pass 1**: Inelastic merging for opposite-charge overlaps
    - Conserves mass, charge, momentum (if mobile)
    - Radius: area-preserving $r_{new} = \sqrt{r_1^2 + r_2^2}$
  - **Pass 2**: Elastic collisions for same-sign overlaps
    - Restitution coefficient e=1 (perfectly elastic)
    - Impulse-based velocity updates
    - Penetration correction along contact normal

**Energy computation**:
- `total_kinetic_energy()`: Sum over mobile particles only
- `total_potential_energy()`: Pairwise Coulomb potential with singularity guard
- Used for monitoring conservation and debugging

**Field evaluation**:
- `electric_field_at_point()`: Superposition of all particle contributions
- Used by field sampler and validation mode
- Applies per-source softening for stability

### `electrosim.rendering.*`
Visualization subsystem organized by concern:

**`rendering.primitives`**:
- Low-level drawing utilities: circles, arrows, lines with anti-aliasing
- Coordinate conversions: world ↔ screen (meters ↔ pixels)
- Reusable geometric primitives for all rendering modules

**`rendering.particles`**:
- Particle rendering with color coding by charge
- Glow effect: Cached radial gradient surfaces
  - Cache key: (size, color, intensity)
  - LRU eviction when cache exceeds limit
- Border overlays: Selection (white) and fixed (gold) indicators

**`rendering.field`**:
- Electric field grid visualization
- Two display modes:
  - **Brightness**: Fixed arrow length, alpha scales with |E|
  - **Length**: Arrow length proportional to |E|, constant alpha
- Grid sampling: Regular lattice at `FIELD_GRID_STEP_PX` spacing
- Alpha surface compositing for smooth blending

**`rendering.field_sampler`**:
- Performance optimization: Pre-compute entire field grid per frame
- `ElectricFieldSampler` class:
  - Builds grid of field vectors once
  - Reused by field visualization and queries
  - Falls back to on-demand evaluation if disabled
- Numba-accelerated grid computation when available

**`rendering.trails`**:
- Trajectory history visualization
- Per-particle trail buffer with timestamps
- Fading: Linear alpha interpolation from max to min
- Anti-aliasing: Double-pass rendering (core + edge)
- Separate trail surface to avoid z-ordering issues

**`rendering.overlay`**:
- HUD information display: FPS, particle count, energy, speed
- Profiling overlay: Per-subsystem timing (physics, field, render)
- Text rendering with drop shadow for readability
- Position: Top-left corner, non-overlapping with simulation

**`rendering.draw`**:
- High-level draw coordinator
- Re-exports drawing functions for convenient imports
- No internal state; pure functional API

### `electrosim.ui.controls`
User input handling and interactive UI elements:

**`InputState` class**:
- Tracks mouse state: position, buttons, modifiers (Shift, Alt, Ctrl)
- Drag tracking: start position, current position, drag vector
- Selected particle index
- Transient UI state: hover target, placement preview

**Event handling**:
- `handle_events()`: Main event dispatcher
  - Mouse clicks: Particle placement with charge/fixed modifiers
  - Drag: Set initial velocity proportional to drag distance
  - Selection: Click existing particle to select
  - Keyboard: Global controls (pause, reset, speed, visualization toggles)
  - Particle editing: Adjust charge/mass/radius of selected particle

**Interactive overlays**:
- Placement preview: Arrow showing initial velocity during drag
- Hover tooltip: Displays world position, local E field, nearest particle info
- Coordinate-aware: Uses world-space for physics, screen-space for rendering

### `main.py`
Application entry point and main loop:

**Initialization**:
- Pygame setup: Window, clock, font
- Create `Simulation` instance
- Create `InputState` instance
- Load default scene

**Frame loop structure**:
```python
while running:
    # 1. Input phase
    handle_events(sim, input_state)
    
    # 2. Physics phase (timed)
    sim.step_frame()  # Multiple RK4 substeps
    
    # 3. Rendering phase
    clear_background()
    draw_grid()
    draw_field_grid()  # If enabled
    draw_particle_glows()
    draw_trails()  # If enabled
    draw_particles()
    draw_vectors()  # Force/velocity if enabled
    draw_placement_preview()
    draw_hover_tooltip()
    
    # 4. Overlay phase
    draw_overlay(fps, energies, profiling)
    
    # 5. Present and throttle
    pygame.display.flip()
    clock.tick(FPS_TARGET)
```

**Web version** (`web/main_web.py`):
- Async main loop for browser compatibility
- Pyodide/WASM adaptations: No timers, async event handling
- Canvas focus management for keyboard input
- Otherwise identical structure to desktop version

## Dependency diagram

NOTE: Use white theme for mermaid diagrams.

```{mermaid}
flowchart LR
    subgraph Simulation
      ENG[simulation.engine]
      PHY[simulation.physics]
    end
    subgraph Rendering
      PRIM[rendering.primitives]
      PART[rendering.particles]
      FIELD[rendering.field]
      FS[rendering.field_sampler]
      TRAIL[rendering.trails]
      OVER[rendering.overlay]
      DRAW[rendering.draw]
    end
    subgraph UI
      CTRL[ui.controls]
    end
    CFG[config]
    MAIN[(main.py)]

    MAIN --> CTRL
    MAIN --> ENG
    MAIN --> DRAW

    ENG <--> PHY
    ENG --> PRIM
    ENG --> PART
    ENG --> FIELD
    ENG --> TRAIL
    ENG --> OVER

    FIELD --> FS
    FIELD --> PRIM

    PART --> PRIM

    CTRL --> ENG
    CTRL --> PRIM

    CFG --> ENG
    CFG --> PHY
    CFG --> PRIM
    CFG --> PART
    CFG --> FIELD
    CFG --> FS
    CFG --> TRAIL
    CFG --> OVER
```

## Data Flow

### Frame Loop Sequence

```{mermaid}
sequenceDiagram
  participant Pygame
  participant UI as UI Controls
  participant Sim as Simulation
  participant Phys as Physics
  participant Draw as Rendering

  Pygame->>UI: poll events
  UI->>Sim: toggle flags / edit particles / placement
  Sim->>Phys: rk4_integrate (substeps)
  Phys-->>Sim: updated positions/velocities
  Sim->>Phys: resolve_collisions
  Sim->>Sim: wrap positions, recompute energies, trails
  Sim->>Draw: pass particles, forces, flags
  Draw-->>Pygame: paint frame
```

### Data Structures

**Particle representation**:
- Python: `Particle` dataclass with NumPy arrays
- Numba kernels: Structure-of-arrays (SoA) packing
  - Separate arrays: `pos_x`, `pos_y`, `vel_x`, `vel_y`, `charge`, `mass`, `radius`, `fixed`
  - Enables SIMD vectorization and cache-friendly access patterns

**State ownership**:
- `Simulation.particles`: List of `Particle` objects (authoritative source)
- Rendering subsystems: Read-only access to particle list
- Physics kernels: Temporary copies for computation, write back to particles

**Trail management**:
- Per-particle circular buffer: Fixed capacity (based on `TRAJECTORY_HISTORY_SECONDS`)
- Automatic pruning: Old positions removed when exceeding duration
- Stored in `Simulation.particle_trails` dictionary keyed by particle ID

### Performance Characteristics

**Time complexity per frame**:
- Force computation: O(N²) where N = particle count
- RK4 integration: O(N × substeps) × 4 stages = O(N)
- Collision detection: O(N²) naive pairwise (no spatial partitioning)
- Field grid: O(M × N) where M = grid points (~400 for default settings)
- Rendering particles: O(N)
- Rendering trails: O(N × history_length)

**Bottlenecks**:
1. **Physics**: Dominates when N > 20, scales quadratically
2. **Field visualization**: Expensive with many particles, disabled by default for performance
3. **Glow rendering**: Alpha blending overhead, cached surfaces help

**Optimization strategies**:
- Numba JIT compilation for physics kernels (5-10× speedup)
- Parallel acceleration with `prange` (additional 2-4× on multi-core)
- Field sampler caching (compute once, reuse for rendering)
- Glow surface cache (avoid regenerating radial gradients)
- Early exits: Skip neutral/fixed/massless particles in tight loops

## Design Patterns

### Configuration as Constants
All tunable parameters are module-level constants in `config.py`:
- **Pro**: Simple, fast access, no runtime overhead
- **Con**: Requires restart to change; no per-simulation settings
- **Rationale**: Prioritizes performance; configuration rarely changes during use

### Dataclass for Particles
`Particle` uses Python 3.7+ dataclass:
- **Advantages**: Automatic `__init__`, `__repr__`, type hints
- **Fields**: Mutable (positions/velocities updated in-place for efficiency)
- **NumPy integration**: Position/velocity as `np.ndarray` for vectorization

### Separation of Concerns
Clear module boundaries:
- **Physics**: No rendering code, pure numerical computation
- **Rendering**: No physics logic, only visualization
- **Controls**: Translates user input to simulation commands
- **Main**: Orchestrates but delegates all work

### Graceful Degradation
Multiple fallback paths:
- **Numba unavailable**: Fall back to pure NumPy/Python (slower but functional)
- **Field sampler disabled**: Compute field on-demand per arrow
- **Low performance**: Disable expensive features (glow, field, trails)

### Immutable Constants
Configuration module uses uppercase naming and type hints:
- Signals "read-only" intent (not enforced, but convention)
- Type annotations enable static checking and IDE autocomplete

## Extension Points

### Adding a New Force
To implement additional forces (e.g., gravity, magnetic):

1. **Add force function** to `electrosim.simulation.physics`:
   ```python
   def magnetic_force_pair(p_i, v_i, q_i, p_j, v_j, q_j, B_field):
       # Lorentz force: F = q(v × B)
       ...
   ```

2. **Integrate in acceleration kernel**:
   - Modify `compute_accelerations()` to include new force
   - Update Numba kernels (serial and parallel variants)

3. **Add configuration** to `electrosim.config`:
   ```python
   MAGNETIC_FIELD_TESLA = (0.0, 0.0, 1.0)  # B_z field
   ```

4. **Test**: Validate with known analytical solution (e.g., cyclotron motion)

### Adding Visualization Modes
To add new visualization overlays:

1. **Create rendering function** in new or existing `rendering.*` module:
   ```python
   def draw_energy_contours(screen, particles, config):
       # Draw equipotential lines
       ...
   ```

2. **Add toggle in controls**: Update `handle_events()` for keyboard shortcut

3. **Integrate in main loop**: Call drawing function when enabled

4. **Add configuration**: Colors, line widths, sampling resolution

### Custom Integrators
To experiment with different time integrators:

1. **Implement in physics module**:
   ```python
   def verlet_integrate(particles, dt, substeps, world_size):
       # Velocity Verlet algorithm
       ...
   ```

2. **Swap in Simulation**: Replace `rk4_integrate()` call in `step_frame()`

3. **Compare**: Energy conservation, performance, accuracy

## Error Handling

**Particle limits**:
- Maximum count enforced: `MAX_PARTICLES` (default 100)
- Prevents memory exhaustion and UI freeze

**Charge/mass/radius bounds**:
- Clamped to `[MIN_*, MAX_*]` ranges in configuration
- Prevents numerical instabilities and visual artifacts

**Collision singularities**:
- Softening prevents infinite forces at r=0
- Penetration correction ensures particles separate

**Periodic boundary wrapping**:
- Positions clamped to `[0, WORLD_*_M)` after each step
- Minimum-image displacement for forces across boundaries

**Energy monitoring**:
- Displayed in overlay for sanity checking
- Large jumps indicate bugs (collision, force, or integrator errors)

## Platform-Specific Adaptations

### Desktop (Windows/Linux/macOS)
- Native Pygame window with hardware acceleration
- Numba JIT compilation available (LLVM backend)
- Blocking event loop with vsync timing

### Web (Pyodide/WASM)
- Pygame-CE rendering to HTML5 Canvas
- No Numba (fallback to NumPy/Python)
- Async event loop (`asyncio` compatible)
- Manual keyboard bridging via JavaScript
- Performance: 2-5× slower than desktop

### Configuration overrides
Web version uses `web/config_web.py` to adjust defaults:
- Lower FPS target (reduce CPU load)
- Simpler visualization defaults
- Disabled profiling overlay (clutter on small screens)

## Testing Strategy

**Unit tests** (recommended, not currently implemented):
- Physics functions: `minimum_image_displacement`, `electric_force_pair`
- Collision resolution: momentum/energy conservation
- Coordinate conversions: world ↔ screen consistency

**Integration tests**:
- Validation mode: Uniform field trajectory accuracy
- Energy conservation: Long-run stability
- Collision sequences: Multi-particle interactions

**Visual regression**:
- Screenshot comparison for rendering correctness
- Field visualization patterns
- Particle appearance (color, glow, borders)

**Performance regression**:
- Benchmarking: FPS vs. particle count
- Profiling: Physics, field, rendering times
- Memory usage: Trail buffers, glow cache

See [Validation](validation.md) for detailed testing documentation.

## Related Documentation

- [Physics Overview](physics_overview.md) — Physical models and equations
- [Performance Notes](performance.md) — Optimization techniques and bottlenecks
- [Web Integration](web_integration.md) — Browser-specific adaptations
- {mod}`electrosim.simulation.engine` — Simulation orchestrator
- {mod}`electrosim.simulation.physics` — Physics kernels
- {mod}`main` — Desktop entry point

