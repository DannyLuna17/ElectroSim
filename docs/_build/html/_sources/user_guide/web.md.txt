# Running ElectroSim on the Web

ElectroSim can run fully in the browser using Python compiled to WebAssembly via Pyodide.
This section explains how to launch, what changed relative to desktop, and how inputs work.

## Quick Start

```bash
cd web
python server.py
# open http://localhost:8000
```

Click "Start Simulation" and wait for the Python environment to finish loading (first time about 30–60s).

## What Runs in the Browser

- Python interpreter (Pyodide) with NumPy/SciPy
- Pygame Community Edition (pygame-ce) rendering to an HTML5 canvas
- Original ElectroSim simulation code (no JS rewrite)

## Keyboard and Mouse Controls

- Same as desktop (see User Guide → Controls)
- The canvas must have focus to receive keys
  - It gets focus automatically on Start; click the canvas if keys don't respond
- Supported keys: `P`, `R`, `C`, `E`, `F`, `V`, `T`, `1-4`, `Delete`, `Space`, `Q/W/A/S/Z/X`

## Differences vs Desktop

- Performance is lower than native (2–5× slower typical)
- Numba acceleration is unavailable in-browser; physics and field sampling automatically fall back
- Audio is disabled by default in browser builds

## Troubleshooting

- If keys don't work, click the canvas to focus it and try again
- First load is slow due to package downloads; subsequent loads use cache
- Check browser console for errors; see Developer Guide → Web Integration for details
