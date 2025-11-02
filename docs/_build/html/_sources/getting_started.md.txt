# Getting Started

This guide walks you through installing and running ElectroSim on desktop and web platforms.

## System Requirements

### Desktop Version

- **Operating System**: Windows, Linux, or macOS
- **Python**: 3.x
- **RAM**: Minimum 2 GB, recommended 4 GB+
- **Display**: 1280×800 or higher resolution
- **GPU**: Not required (CPU-only simulation)

### Web Version

- **Browser**: Chrome 90+, Firefox 88+, Safari 15+, or Edge 90+
- **RAM**: Minimum 300 MB available for browser tab
- **Internet**: Required for first load (~50-60 MB download)
- **JavaScript**: Must be enabled
- **WebAssembly**: Must be supported (enabled by default in modern browsers)

## Quick Start (Choose Your Platform)

### Option 1: Web Version (Easiest - No Installation)

**Try the live demo**: [https://electro-sim.vercel.app/](https://electro-sim.vercel.app/)

1. Open the link in a modern browser
2. Wait for Pyodide and packages to load (30-60 seconds first time)
3. Click "Start Simulation"
4. Place particles with mouse, control with keyboard

That's it. No installation required.

### Option 2: Desktop Version (Best Performance)

**Full installation with Python environment:**

#### Step 1: Clone or Download Repository

If using git:
```powershell
git clone https://github.com/DannyLuna17/ElectroSim.git
cd ElectroSim
```

Or download and extract the ZIP file, then navigate to the directory.

#### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS (bash/zsh):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Note**: If PowerShell execution policy prevents activation:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `pygame>=2.6.1` - Graphics and windowing
- `numpy>=2.0.0` - Numerical arrays and linear algebra
- `scipy` - Scientific computing (special functions)
- `numba>=0.59` - JIT compilation for physics kernels
- `intel-cmplr-lib-rt` - Intel compiler runtime (optional optimization)

**Troubleshooting installation:**

If pip fails to install, try:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

If Numba fails on your platform:
- ElectroSim will fall back to pure NumPy (slower but functional)
- Remove `numba` from `requirements.txt` if installation is problematic

#### Step 4: Run ElectroSim

```powershell
python main.py
```

A window should open with the simulation. You'll see:
- Dark background
- One particle in the center
- FPS counter and energy display in top-left corner

**First run tips:**
- Use mouse to place particles (click and drag)
- Press `E` to toggle electric field visualization
- Press `P` to pause/resume
- Press `F` to show force vectors
- Press `V` to show velocity vectors
- See controls below for full list

## Platform-Specific Notes

### Windows

ElectroSim was developed primarily on Windows. Everything should work out of the box.

**If you encounter DLL errors:**
- Install [Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
- Update graphics drivers

### Linux

Python 3.x is usually available via package manager:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip
```

Then follow standard installation steps.

**Note on Numba**: Linux usually has excellent Numba support via LLVM.

### macOS

Use Homebrew to install Python:
```bash
brew install python@3.11
```

Then follow standard installation steps.

**Apple Silicon (M1/M2/M3/M4)**: Numba may have limited support on ARM architecture. If installation fails, remove `numba` and `intel-cmplr-lib-rt` from requirements and run without JIT acceleration (slightly slower but fully functional).

## Running ElectroSim Locally (Web Version)

You can run the web version on localhost for development or offline use:

### Step 1: Navigate to Web Directory

```powershell
cd web
```

### Step 2: Start Development Server

```powershell
python server.py
```

You should see:
```
ElectroSim Web Server
Serving at http://localhost:8000
Directory: C:\path\to\ElectroSim\web
Open http://localhost:8000
Press Ctrl+C to stop
```

### Step 3: Open in Browser

Navigate to `http://localhost:8000` in your browser.

**First load:**
- Status messages show package download progress
- Pyodide (~7 MB)
- NumPy (~15 MB)
- SciPy (~25 MB)
- pygame-ce (~5 MB)
- Total time: 30-60 seconds depending on connection

**After first load:**
- Browser caches all packages
- Subsequent loads are fast (2-5 seconds)

### Step 4: Start Simulation

Click "Start Simulation" button when it becomes active.

### Stopping the Server

Press `Ctrl+C` in the terminal where `server.py` is running.

## Verifying Installation

### Desktop Version

After `python main.py`, you should see:

1. **Window opens** (1280×800 pixels)
2. **Default scene loads** with a few particles
3. **FPS display** in top-left corner (should be ~60 FPS)
4. **Particle interactions** visible (particles orbiting, attracting, repelling)

**Test basic functionality:**
- Click to place a particle → New particle appears at click position
- Shift+Click → Blue (negative) particle appears
- Press `E` → Electric field grid appears
- Press `P` → Simulation pauses
- Press `R` → Scene resets to default

If all these work, installation is successful.

### Web Version

After clicking "Start Simulation", you should see:

1. **Canvas activates** with simulation rendering
2. **Default particles** visible and moving
3. **FPS display** in overlay (may be lower than desktop, 30-60 FPS typical)
4. **Responsive controls** (click, keyboard)

**Test basic functionality:**
- Click canvas to place particle
- Press `E` to toggle field (may be slow with many particles)
- Press `P` to pause
- Press `R` to reset

If controls work and particles interact, web version is functional.

## Building Documentation (Optional)

Full documentation is pre-built in `docs/_build/html/`. To rebuild from source:

### Step 1: Install Documentation Dependencies

```powershell
pip install -r docs/requirements-docs.txt
```

This installs:
- Sphinx - Documentation generator
- MyST-Parser - Markdown support in Sphinx
- Furo theme - Clean modern Sphinx theme
- Various Sphinx extensions

### Step 2: Build HTML Documentation

```powershell
python -m sphinx -b html docs docs/_build/html
```

Build output will be in `docs/_build/html/`.

### Step 3: Open Documentation

**Windows:**
```powershell
start docs/_build/html/index.html
```

**Linux:**
```bash
xdg-open docs/_build/html/index.html
```

**macOS:**
```bash
open docs/_build/html/index.html
```

Or manually navigate to `docs/_build/html/index.html` in your file browser.

### Cleaning Documentation Build

To rebuild from scratch:

```powershell
python -m sphinx -M clean docs docs/_build
python -m sphinx -b html docs docs/_build/html
```

## Updating the Web Deployment

If you modify the desktop code and want to update the web version:

### Step 1: Run Deployment Script

```powershell
python deploy_web.py
```

This copies the latest `electrosim/` package to `web/electrosim/`.

### Step 2: Test Locally

```powershell
cd web
python server.py
# Open http://localhost:8000 and test
```

## Common Issues and Solutions

### Desktop Issues

**"No module named pygame/numpy/numba"**
```powershell
pip install -r requirements.txt
```

Make sure virtual environment is activated.

**Window opens but is black/frozen**
- Update graphics drivers
- Try disabling hardware acceleration
- Check console for error messages

**"ImportError: DLL load failed"** (Windows)
- Install Visual C++ Redistributable
- Reinstall Python with "pip" and "tcl/tk" options enabled

**Numba installation fails**
- Remove `numba` and `intel-cmplr-lib-rt` from `requirements.txt`
- Install remaining packages: `pip install pygame numpy scipy`
- ElectroSim will detect missing Numba and fall back automatically

**Simulation is very slow (< 30 FPS with few particles)**
- Enable `FIELD_SAMPLER_ENABLED = True` in `electrosim/config.py`
- Enable `NUMBA_PARALLEL_ACCEL = True` if Numba is installed
- Disable field visualization (press `E`) for testing
- Check Task Manager - close other CPU-intensive programs

### Web Issues

**"Failed to load Pyodide"**
- Check internet connection
- Try different browser
- Clear browser cache and retry
- Check browser console (F12) for specific error

**Very slow loading**
- First load downloads ~50-60 MB
- Check network speed
- Subsequent loads use cache (much faster)
- Consider using desktop version if network is unreliable

**Keyboard doesn't work**
- Click the canvas to focus it (white border appears)
- Some browsers capture certain keys (F1, F11, Ctrl+W, etc.)
- Check browser console for "KeyboardEvent" errors

**Simulation crashes/freezes**
- Reduce particle count (< 20 recommended for web)
- Close other browser tabs to free memory
- Refresh page to reset
- Try desktop version for better performance

### Both Platforms

**Particles behaving strangely**
- Physics is deterministic; strange behavior is usually correct
- Periodic boundaries cause wrapping (particles reappear on opposite side)
- Press `R` to reset to known-good default scene
- Check that you haven't accidentally created overlapping particles

**Energy not conserving**
- Small energy drift is normal (numerical error accumulation)
- Large energy changes indicate collisions or merging
- Opposite charges merge on contact (energy changes)
- Check overlay: E_tot should be relatively stable over time

## Next Steps

Now that ElectroSim is running:

1. **Learn the controls**: See [User Guide → Controls](user_guide/controls.md)
2. **Understand visualization**: See [User Guide → Visualization](user_guide/visualization.md)
3. **Configure settings**: See [User Guide → Configuration](user_guide/configuration.md)
4. **Explore the physics**: See [Developer Guide → Physics Overview](developer_guide/physics_overview.md)
5. **Read the math**: See [Mathematical Foundations](math/coulomb_periodic.md)

## Getting Help

**Documentation:**
- This guide and other docs in `docs/`
- README files in project root and `web/`
- Code comments and docstrings

**Debugging:**
- Check console output for error messages
- Enable `PROFILE_OVERLAY_ENABLED = True` to see performance metrics
- Read [Developer Guide → Validation](developer_guide/validation.md) for testing approaches

**Performance tuning:**
- See [Developer Guide → Performance](developer_guide/performance.md)
- Adjust settings in `electrosim/config.py`
- Web version: see `web/config_web.py` overrides

Happy simulating!
