# ElectroSim

<p align="center">
  <img src="assets/logoElectro.png" alt="ElectroSim logo" width="480">
</p>

Interactive 2D charged particle simulator featuring real-time electromagnetic interactions under Coulomb's law with superposition, fixed-step RK4 integration, elastic collisions, and a periodic 2D domain. Visualize electric fields, forces, velocities, and particle trajectories in real time.

> [!IMPORTANT]
> **Live Demo**: https://electro-sim.vercel.app/ | **Documentation**: https://electro-sim-docs.vercel.app/

## Downloads

- **Windows (x64)**: [Latest release build](https://github.com/DannyLuna17/ElectroSim/releases/latest)

<p align="center">
  <img src="assets/ss.png" alt="ElectroSim screenshot showing particles, field vectors, and trails" width="800">
</p>

## Features

- **Accurate Physics Simulation**: N-body electromagnetic interactions with Coulomb's law and superposition principle
- **RK4 Integration**: Fourth-order Runge-Kutta time integration for precise trajectory computation
- **Periodic Boundary**: 2D toroidal domain with minimum image convention for seamless wrapping
- **Collision Detection**: Elastic collisions between charged particles with inelastic merging for opposite charges
- **Rich Visualization**: Real-time rendering of electric field vectors, force arrows, velocity vectors, and fading particle trails
- **Interactive Controls**: Click-and-drag particle placement, real-time editing, and keyboard shortcuts
- **Web Version**: Full simulation runs in browser using Pyodide (Python in WebAssembly)
- **Performance Optimized**: Numba JIT compilation for physics kernels and optional field sampling cache

## Quick Start

### Desktop Version

#### Requirements

- **Python**: 3.x
- **Dependencies**: pygame, numpy, scipy, numba

#### Installation

```powershell
cd ElectroSim
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or: source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

#### Run

```powershell
python main.py
```

### Web Version

The web version runs entirely in your browser with no installation required.

**Live Demo**: [https://electro-sim.vercel.app/](https://electro-sim.vercel.app/)

Or run locally:

```powershell
cd web
python server.py
# Open http://localhost:8000 in your browser
```

First load takes 30-60 seconds to download Pyodide and scientific libraries. Click "Start Simulation" when ready.

## Controls

### Particle Placement

- **Left Click**: Place positive particle (drag to set initial velocity)
- **Shift + Click**: Place negative particle
- **Alt/Ctrl + Click**: Place fixed (immobile) particle
- **Click on Particle**: Select for editing

### Particle Editing (when selected)

- **Q/W**: Decrease/increase charge by 1 µC
- **A/S**: Decrease/increase mass by 0.005 kg
- **Z/X**: Decrease/increase radius by 0.005 m
- **Space**: Toggle fixed state
- **Delete/Backspace**: Remove particle

### Global Controls

- **P**: Pause/resume simulation
- **R**: Reset to default scene
- **C**: Clear all particles
- **1/2/3/4**: Set simulation speed (0.5×/1×/2×/4×)

### Visualization Toggles

- **E**: Toggle electric field visualization
- **M**: Switch field mode (brightness vs. length)
- **F**: Toggle force vectors
- **V**: Toggle velocity vectors
- **T**: Toggle particle trajectories
- **G**: Toggle metric grid (meters)
- **B**: Toggle particle glow effect

## Physics Model

### Core Principles

ElectroSim implements a physically accurate electromagnetic N-body simulation:

- **SI Units**: All quantities in meters, kilograms, coulombs, newtons, seconds
- **Coulomb Constant**: k = 8.9875517873681764×10⁹ N·m²/C²
- **Domain**: 16.0 m × 10.0 m periodic (toroidal) space with 1 m = 80 pixels
- **Time Step**: Fixed dt = 0.001 s with adaptive substeps (4/8/16/32) based on speed setting

### Integration Method

- **Runge-Kutta 4th Order (RK4)**: Numerical integration with O(dt⁴) local error
- **Fixed Time Step**: Consistent 1 ms timestep for stability
- **Substep Multiplication**: Higher speeds increase substeps per frame, not dt

### Forces and Interactions

- **Coulomb Force**: F = k·q₁·q₂/r² with superposition for multiple particles
- **Minimum Image Convention**: Uses nearest periodic image for force calculation
- **Plummer Softening**: Short-range regularization ε = 0.1 × (r₁ + r₂) prevents singularities
- **Superposition**: Total force on each particle is vector sum of all pairwise interactions

### Collisions

- **Elastic Collisions**: 2D hard disk collisions with restitution coefficient = 1.0
- **Penetration Correction**: Mass-weighted separation when particles overlap
- **Inelastic Merges**: Opposite-sign charges merge on collision (conserving mass, charge, momentum)
- **Fixed Particles**: Immobile particles reflect mobile ones without moving

### Energy Conservation

- **Kinetic Energy**: E_kin = Σ ½mv²
- **Potential Energy**: E_pot = Σ k·qᵢ·qⱼ/rᵢⱼ (pairwise sum with periodic corrections)
- **Total Energy**: E_tot = E_kin + E_pot (monitored in overlay for validation)

## Visualization

### Electric Field

- **Grid Sampling**: Configurable resolution (default: 30 pixel spacing)
- **Two Display Modes**:
  - **Brightness Mode**: Fixed-length arrows with color intensity ∝ |E|
  - **Length Mode**: Variable-length arrows with length ∝ |E|
- **Field Sampler**: Optional precomputed field grid cache (toggle in `config.py`)

### Particle Rendering

- **Color Coding**: Red (positive), blue (negative), white (neutral)
- **Glow Effect**: Soft radial gradient with intensity proportional to |charge|
- **Selection Highlight**: White border around selected particle
- **Fixed Indicator**: Gold border for immobile particles

### Vectors and Trails

- **Force Vectors**: Yellow arrows showing net electromagnetic force
- **Velocity Vectors**: Green arrows showing instantaneous velocity
- **Trajectories**: Fading polyline trails (configurable history duration, default 3 seconds)

### Overlay Information

Real-time display shows:
- **FPS**: Frames per second
- **N**: Number of particles
- **Speed**: Current simulation speed multiplier
- **dt**: Integration timestep
- **Substeps**: Number of RK4 steps per frame
- **Energies**: Kinetic, potential, and total energy
- **Profile**: Per-frame timing breakdown (physics, field, rendering)

## Configuration

All simulation parameters are centralized in `electrosim/config.py`:

### Window Settings

- `WINDOW_WIDTH_PX`: Window width (default: 1280)
- `WINDOW_HEIGHT_PX`: Window height (default: 800)
- `FPS_TARGET`: Target frame rate (default: 60)

### Physics Parameters

- `K_COULOMB`: Coulomb constant in N·m²/C²
- `DT_S`: Integration timestep in seconds
- `SUBSTEPS_BASE_PER_FRAME`: Base substeps per frame
- `SOFTENING_FRACTION`: Plummer softening as fraction of contact radius

### Particle Defaults

- `DEFAULT_CHARGE_C`: Default charge magnitude (5 µC)
- `DEFAULT_MASS_KG`: Default particle mass (0.02 kg)
- `DEFAULT_RADIUS_M`: Default particle radius (0.1 m)
- `MAX_PARTICLES`: Maximum particle count (100)

### Performance Options

- `FIELD_SAMPLER_ENABLED`: Cache electric field grid (faster for many particles)
- `NUMBA_PARALLEL_ACCEL`: Enable parallel loops in physics kernels
- `NUMBA_FASTMATH`: Allow fast math approximations (slight accuracy tradeoff)
- `PROFILE_OVERLAY_ENABLED`: Show per-frame timing breakdown

### Visualization Options

- `FIELD_VIS_MODE`: Field display mode ("brightness" or "length")
- `GLOW_ENABLED`: Particle glow effect
- `TRAJECTORY_HISTORY_SECONDS`: Trail duration in seconds

## Project Structure

```
ElectroSim/
├── electrosim/ # Core simulation package
│   ├── config.py # Global configuration constants
│   ├── simulation/ # Physics and simulation engine
│   │   ├── physics.py # Force calculations, RK4 integration
│   │   └── engine.py # Main simulation loop and state
│   ├── rendering/ # Visualization modules
│   │   ├── draw.py # High-level drawing coordination
│   │   ├── primitives.py # Basic drawing functions
│   │   ├── field.py # Electric field visualization
│   │   ├── field_sampler.py # Cached field grid computation
│   │   ├── particles.py # Particle rendering with glow
│   │   ├── trails.py # Trajectory trail rendering
│   │   └── overlay.py # HUD and overlay text
│   └── ui/ # User interaction
│       └── controls.py # Mouse/keyboard input handling
├── main.py # Desktop application entry point
├── requirements.txt # Desktop dependencies
├── docs/ # Full documentation (Sphinx)
│   ├── user_guide/ # User documentation
│   ├── developer_guide/ # Architecture and implementation
│   ├── math/ # Mathematical derivations
│   ├── api/ # API reference
│   └── annotated/ # Line-by-line code explanations
└── web/ # Web version (Pyodide)
    ├── index.html # Web interface
    ├── main_web.py # Web-adapted entry point
    ├── config_web.py # Web-specific configuration
    ├── server.py # Development server
    ├── vercel.json # Vercel deployment config
    └── electrosim/ # Copy of core package
```

## Documentation

The latest documentation is hosted at [https://electro-sim-docs.vercel.app/](https://electro-sim-docs.vercel.app/).

Comprehensive documentation is also available in the `docs/` directory, including:

- **User Guide**: Installation, controls, visualization options, configuration
- **Developer Guide**: Architecture, physics implementation, performance optimization, validation
- **Mathematical Foundations**: LaTeX-formatted derivations for all physics equations
- **API Reference**: Auto-generated documentation for all modules
- **Annotated Source**: Line-by-line explanations for every function

### Build Documentation

```powershell
pip install -r docs/requirements-docs.txt
python -m sphinx -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser.

### Documentation Sections

- `docs/getting_started.md` — Installation and first run
- `docs/user_guide/` — Controls, visualization, configuration, web version
- `docs/developer_guide/` — Architecture, physics overview, performance, validation, web integration
- `docs/math/` — Coulomb with PBC, Plummer softening, RK4 derivation, collisions, energy, field mapping
- `docs/api/` — Complete API reference
- `docs/annotated/` — Function-by-function explanations

## Deployment

### Web Deployment

The web version is deployed to Vercel at [https://electro-sim.vercel.app/](https://electro-sim.vercel.app/).

To deploy updates:

```powershell
# Update web files
python deploy_web.py

# Deploy to Vercel
```

The `deploy_web.py` script copies the latest `electrosim/` package to `web/electrosim/`.

## Limitations

### Desktop Version

- Maximum 100 particles (configurable but performance degrades beyond this)
- 2D simulation only (no z-axis)
- No magnetic interactions (purely electrostatic)

### Web Version

- Performance 2-4× slower than native (WebAssembly overhead)
- No Numba JIT compilation (automatic fallback to pure Python)
- Audio disabled (SDL dummy audio driver)
- First load requires ~50MB download (Pyodide + scientific libraries)

## Building a Windows Executable

1. Ensure you have a 64-bit Python 3.x installed and available on `PATH`.
2. From the project root, run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/build_windows_exe.ps1
   ```

   The helper script creates an isolated virtual environment, installs dependencies plus PyInstaller, and bundles the app.
3. The compiled binary will be created at `dist/ElectroSim/ElectroSim.exe`. 

## Troubleshooting

### Desktop Issues

**ImportError: No module named pygame/numpy/numba**
```powershell
pip install -r requirements.txt
```

**Simulation is slow**
- Enable `FIELD_SAMPLER_ENABLED = True` in `config.py`
- Enable `NUMBA_PARALLEL_ACCEL = True` in `config.py`
- Reduce particle count
- Disable field visualization (press E)

**Particles disappear**
- They've wrapped around due to periodic boundaries
- Press R to reset to default scene

### Web Issues

**Page stuck loading**
- Check browser console for errors
- Ensure stable internet connection (first load downloads dependencies)
- Try hard refresh (Ctrl+Shift+R)

**Keyboard not working**
- Click the canvas to focus it
- Check browser console for errors
- See `docs/developer_guide/web_integration.md` for details

**Simulation is very slow**
- Reduce particle count (< 20 recommended)
- Disable field visualization (press E)
- Use lower speed setting (press 1 for 0.5×)

## Acknowledgments

- **Libraries**: pygame, NumPy, SciPy, Numba, Pyodide
- **Inspiration**: [Paul Falstad's Java applets](https://falstad.com/mathphysics.html)

## License

Released under the [MIT License](LICENSE).