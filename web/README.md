# ElectroSim Web Version

Full-featured ElectroSim running entirely in your browser using Python compiled to WebAssembly via [Pyodide](https://pyodide.org/). Zero installation, pure client-side computation with the complete physics simulation, visualization, and interactive controls.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://electro-sim.vercel.app/)

## Live Demo

**Try it now**: [https://electro-sim.vercel.app/](https://electro-sim.vercel.app/)

No installation, no downloads, no backend. Works 100% in your browser.

## Features

- **Full Python in Browser**: Complete CPython 3.11 running in WebAssembly (via Pyodide 0.27.7)
- **Scientific Computing**: NumPy, SciPy work natively with no JavaScript rewrite
- **Pygame Rendering**: pygame-ce renders to HTML5 Canvas using Emscripten SDL2
- **Zero Conversion**: Original desktop Python code runs unchanged
- **Client-Side Only**: All computation happens in your browser, no server required
- **Offline Capable**: After first load, works offline (browser cache)

## Quick Start

### Option 1: Use Live Demo (Recommended)

Just visit [https://electro-sim.vercel.app/](https://electro-sim.vercel.app/) and click "Start Simulation".

### Option 2: Run Locally

1. **Start the development server:**
   ```bash
   cd web
   python server.py
   ```

2. **Open in browser:**
   Navigate to `http://localhost:8000`

3. **Wait for initialization:**
   First load downloads Pyodide and scientific libraries (~50-60 MB).
   Status messages appear in the loading screen.

4. **Start simulation:**
   Click "Start Simulation" when the button becomes active.

## How It Works

### Architecture Overview

ElectroSim Web runs the complete desktop Python codebase in the browser without modification:

1. **Pyodide WebAssembly Runtime**
   - CPython 3.11 compiled to WebAssembly
   - Full Python standard library available
   - Imports work exactly as native Python

2. **Scientific Libraries**
   - NumPy: Compiled to WASM with BLAS/LAPACK
   - SciPy: Full scientific computing stack
   - Both run at near-native speed in WASM

3. **Pygame-CE Integration**
   - pygame-ce (Community Edition) with Emscripten support
   - SDL2 compiled to WASM targets HTML5 Canvas
   - Keyboard/mouse events bridged from DOM to pygame

4. **Simulation Engine**
   - Original `electrosim/` package loaded directly
   - RK4 integration, Coulomb forces, collision detection unchanged
   - Only difference: async main loop (no `pygame.time.set_timer()`)

### Technical Stack

| Component | Technology |
|-----------|-----------|
| Python Runtime | Pyodide 0.27.7 (CPython 3.11 + WASM) |
| Graphics | pygame-ce → Emscripten SDL2 → Canvas |
| Physics | NumPy (BLAS), SciPy |
| Rendering | HTML5 Canvas 2D Context |
| Deployment | Vercel (static hosting with CORS headers) |

### What's Different from Desktop?

**Code Changes:**
- `main_web.py`: Async event loop instead of synchronous (WASM requirement)
- `config_web.py`: Web-optimized settings (smaller window, performance tuning)
- No `pygame.time.set_timer()`: Not supported in WASM, manual loop instead

**Performance:**
- ~2-10× slower than native (WebAssembly overhead)
- Numba JIT disabled (unavailable in browser)
- Field sampler uses Python fallback (no compiled kernels)

**Features Disabled:**
- Audio output (SDL dummy audio driver)
- Multi-threading (single-threaded WASM environment)

## Performance Notes

### First Load (30-60 seconds)

The initial page load downloads:
- Pyodide runtime (~7 MB)
- NumPy (~15 MB)
- SciPy (~25 MB)
- pygame-ce (~5 MB)
- Miscellaneous dependencies (~3 MB)

Total: ~50-60 MB, heavily compressed.

**Progress indicators** show package loading status.

### Subsequent Loads (2-5 seconds)

Browser caches all packages. Reloading is fast.

**Recommendations for Web:**
- Keep particle count < 20 for smooth 60 FPS
- Disable field visualization for better performance (press E)
- Use brightness mode instead of length mode (faster)

## File Structure

```
web/
├── index.html # Main web interface and Pyodide loader
├── main_web.py # Web entry point (async loop, no timers)
├── config_web.py # Web-specific config (FPS, window size, performance)
├── server.py # Local development server (CORS headers)
├── vercel.json # Vercel deployment config (headers, static build)
├── .vercelignore # Exclude dev files from deployment
├── requirements-web.txt # Package list (for reference, loaded by Pyodide)
└── electrosim/ # Complete ElectroSim package (copied from ../electrosim/)
    ├── config.py # Core configuration
    ├── simulation/ # Physics engine
    │   ├── physics.py # Force calculations, RK4 integration
    │   └── engine.py # Simulation state and step logic
    ├── rendering/ # Visualization
    │   ├── draw.py # High-level drawing
    │   ├── field.py # Electric field rendering
    │   ├── field_sampler.py # Field grid cache
    │   ├── particles.py # Particle glow and rendering
    │   ├── trails.py # Trajectory trails
    │   └── overlay.py # HUD overlay
    └── ui/ # Input handling
        └── controls.py # Mouse/keyboard events
```

## Controls

All desktop controls work in the browser:

### Particle Placement
- **Left Click**: Place positive particle (drag to set velocity)
- **Shift + Click**: Place negative particle
- **Alt/Ctrl + Click**: Place fixed (immobile) particle

### Particle Editing (when selected)
- **Q/W**: Decrease/increase charge by 1 µC
- **A/S**: Decrease/increase mass by 0.005 kg
- **Z/X**: Decrease/increase radius by 0.005 m
- **Space**: Toggle fixed state
- **Delete/Backspace**: Remove particle

### Global Controls
- **P**: Pause/resume
- **R**: Reset to default scene
- **C**: Clear all particles
- **1/2/3/4**: Speed (0.5×/1×/2×/4×)

### Visualization Toggles
- **E**: Electric field
- **M**: Field mode (brightness/length)
- **F**: Force vectors
- **V**: Velocity vectors
- **T**: Trajectories
- **G**: Metric grid
- **B**: Particle glow

**Important**: The canvas must have focus to receive keyboard input. Click the canvas once if keys don't respond.

## Troubleshooting

### Loading Issues

**Stuck on "Loading Pyodide..."**
- Check browser console (F12) for errors
- Ensure stable internet connection
- Try clearing browser cache and hard refresh (Ctrl+Shift+R)
- Check browser compatibility (Chrome/Edge 90+, Firefox 88+, Safari 15+)

**"Failed to load package" errors**
- CDN may be temporarily unavailable
- Wait a few minutes and try again
- Check if browser extensions (ad blockers) are interfering

**Blank screen after "Start Simulation"**
- Check console for Python errors
- Ensure WebAssembly is enabled (should be default)
- Try incognito/private mode to rule out extensions

### Performance Issues

**Simulation is very slow (< 20 FPS)**
- Reduce particle count (aim for < 15 particles)
- Disable electric field visualization (press E)
- Disable particle glow (press B)
- Use lower speed setting (press 1 for 0.5×)
- Close other tabs to free memory

**Browser becomes unresponsive**
- Particle count likely too high (> 30)
- Press C to clear all particles
- Refresh page to reset

### Keyboard Issues

**Keys not working**
- Click the canvas to focus it
- Canvas has a white border when focused
- Some keys may be captured by browser (F11, Ctrl+W, etc.)

**Specific key doesn't work**
- Check browser console for "KeyboardEvent bridge" messages
- Some browser/OS combos may not forward certain keys
- Try using mouse controls as alternative

### Physics/Rendering Issues

**Particles behaving strangely**
- Physics is identical to desktop version
- Periodic boundaries may appear strange initially
- Press R to reset to known-good default scene

**Field visualization not appearing**
- Press E to toggle (may be off by default)
- Check console for rendering errors
- Field computation is expensive; try with fewer particles first

**Particle colors wrong**
- Ensure browser color management is standard sRGB
- Try different browser

## Development

### Local Development Workflow

1. **Edit source files** in `../electrosim/` (desktop version)
2. **Update web copy**:
   ```bash
   python ../deploy_web.py
   ```
3. **Test locally**:
   ```bash
   cd web
   python server.py
   ```
4. **Hard refresh browser** (Ctrl+Shift+R) to bypass cache

### Modifying Web-Specific Code

**index.html** - Bootstrap and Pyodide loading:
- Pyodide initialization
- Package loading sequence
- Keyboard event bridge
- Canvas setup and SDL environment

**main_web.py** - Web entry point:
- Async main loop (`asyncio.create_task()`)
- Fallback for missing pygame
- Integration with `config_web.py`

**config_web.py** - Web-specific settings:
- Smaller window size (1100×480 instead of 1280×800)
- Performance tuning (FPS target, field sampler settings)
- Feature flags (`WEB_MODE = True`)

**Required HTTP Headers** (for SharedArrayBuffer/WASM threads):
```
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Opener-Policy: same-origin
Access-Control-Allow-Origin: *
```

These are set in `vercel.json` and `server.py`.

**Minimum Requirements:**
- WebAssembly support (all modern browsers)
- HTML5 Canvas 2D
- ES6+ JavaScript
- ~300 MB RAM available

## Advanced Topics

### Debugging Python Code in Browser

1. Open browser console (F12)
2. Python `print()` statements appear in console
3. Check "PyodideConsole" for Python errors
4. Use `console.log()` from Python: `js.console.log("message")`

### Performance Profiling

Enable profile overlay in `config_web.py`:
```python
PROFILE_OVERLAY_ENABLED = True
```

Shows per-frame timing:
- Physics computation
- Field grid calculation
- Rendering (draw calls)
- Total frame time

### Memory Management

Browser tab memory is limited. Tips:
- Clear particles regularly (press C)
- Reduce trajectory history in config
- Disable field visualization when not needed
- Close other tabs

### Offline Usage

After first load, browser caches packages. To enable offline:
1. Load page once with internet
2. Wait for full initialization

## Limitations

### Hard Limitations (Cannot Fix)
- No Numba JIT compilation
- No multi-threading (single WASM thread)
- Audio not supported
- Performance ~2-10× slower than native

### Soft Limitations (Could Improve)
- Touch controls not optimized (mobile UX)
- Large particle counts slow (< 20 recommended)
- First load time (package downloads)

## Related Documentation

- **Main README**: `../README.md` - Desktop version documentation
- **Developer Guide**: `../docs/developer_guide/web_integration.md` - Technical details
- **User Guide**: `../docs/user_guide/web.md` - Web-specific user docs
- **Pyodide Docs**: [pyodide.org](https://pyodide.org/) - Python in browser
- **pygame-ce**: [pygame-ce.github.io](https://pyodide.org/en/stable/usage/packages-in-pyodide.html) - Pygame Community Edition

## Support

**Issues?**
- Check browser console (F12) first
- Read troubleshooting section above
- See main documentation: `../docs/`
- Verify desktop version works (to isolate web-specific issues)

**Feature Requests?**
- Ensure feasible in WebAssembly environment
- Check if desktop version has it already
- Consider performance impact
