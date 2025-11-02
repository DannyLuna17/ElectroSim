# Web Integration (Pyodide + pygame-ce)

This document describes how ElectroSim runs in the browser, the added modules, and
how browser-specific concerns are handled.

## Components and Data Sources

- `web/index.html`
  - Loads Pyodide (0.27.7), NumPy, SciPy, and `pygame-ce`
  - Creates the HTML5 `canvas#canvas` target
  - Binds the Emscripten Module canvas to the DOM canvas
  - Sets SDL/pygame environment variables (display target, keyboard element, dummy audio)
  - Implements an async bootstrap: package load → file load → init → start

- `web/main_web.py`
  - Web-adapted entrypoint that leverages the existing desktop simulation
  - Uses `pygame-ce` to render into the canvas
  - Runs an async-friendly frame loop (no `set_timer`, not supported on WASM)
  - Gracefully degrades if optional rendering pieces are unavailable

- `web/config_web.py`
  - Overrides certain defaults for web (e.g., FPS, profiling overlay, sampler defaults)
  - Imported by `main_web.py` instead of desktop `config.py`

- `web/server.py`
  - Simple HTTP static server for local development

- `web/electrosim/`
  - A copy of the Python package so Pyodide can import the modules

## Keyboard Input Bridging

SDL’s built-in DOM bridge may try to use missing symbols on some browsers. We:

- Set `SDL_HINT_EMSCRIPTEN_KEYBOARD_ELEMENT` to `#canvas` so events are scoped
- Focus the canvas on Start and make it focusable (`tabindex=0`)
- Add a JavaScript bridge that captures `keydown` / `keyup` at capture phase
  and posts equivalent `pygame.event` KEYDOWN/KEYUP events to the Python side
- This avoids the missing symbol path and preserves the desktop control scheme

## Field Sampling Fallback

Numba kernels are not available in Pyodide. The field sampler:

- Tries to import `_compute_field_grid_numba`
- If unavailable, computes the electric field per grid-point using `electric_field_at_point`
- Expected behavior: same visuals at lower performance

## Expected Behavior (Web)

- Simulation runs at the configured `FPS_TARGET` (default 60) with async loop
- Keyboard/mouse behave like desktop when the canvas is focused
- Visuals: particles, trails, vectors, overlays identical to desktop
- Performance: 2–10× slower than native; keep particle count modest

## Limitations

- Audio is disabled (SDL dummy driver)
- Timers (`set_timer`) are not supported; use an explicit loop
- Numba acceleration disabled; kernels fall back to Python

## Debugging Tips

- Open browser console to inspect logs and Python prints
- Verify the canvas is focused if keys don’t work
- Use the overlay (enable in `config_web.py`) to view frame timing
