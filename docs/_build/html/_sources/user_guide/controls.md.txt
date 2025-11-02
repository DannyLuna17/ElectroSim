# Controls

ElectroSim uses a single-button mouse workflow combined with a handful of keyboard shortcuts. Modifiers can be combined: for example, holding `Shift+Ctrl` while placing creates a fixed negative particle.

## Mouse

- **Left click + release on empty space**: Start and finish a particle placement. Drag before release to set initial velocity based on drag vector.
  - Hold `Shift` while clicking to place a negative (blue) particle.
  - Hold `Alt` or `Ctrl` to place the particle as fixed. Modifiers stack with `Shift`.
- **Left click on a particle**: Select the closest particle under the cursor.
- **Drag a selected particle**: Reposition it; ElectroSim temporarily fixes the particle while you drag and restores its previous fixed/velocity state on release.

## Keyboard

### Simulation Flow
- `P`: Pause or resume integration.
- `R`: Reset to the default single-particle scene.
- `C`: Clear all particles.
- `Esc`: Quit ElectroSim.

### Speed Control
- `1 / 2 / 3 / 4`: Switch to 0.5× / 1× / 2× / 4× simulation speed multipliers.

### Visualization Toggles
- `E`: Toggle electric field visualization.
- `M`: Switch field mode between brightness and length scaling.
- `F`: Toggle force vectors.
- `V`: Toggle velocity vectors.
- `T`: Toggle trajectory trails.
- `G`: Toggle the metric grid overlay.
- `B`: Toggle glow rendering.
- `O`: Toggle the main overlay (HUD + profiling panel).
- `I`: Toggle the hover tooltip.

### Particle Editing
- `Space`: Toggle the fixed/mobile state on the selected particle.
- `Delete` / `Backspace`: Remove the selected particle.
- `Q` / `W`: Decrease or increase charge by `1 µC` (`CHARGE_STEP_C`).
- `A` / `S`: Decrease or increase mass by `0.005 kg` (`MASS_STEP_KG`).
- `Z` / `X`: Decrease or increase radius by `0.005 m` (`RADIUS_STEP_M`).

### Validation
- `U`: Start the uniform electric-field validation harness (replaces the current scene until it finishes).

The hover tooltip (toggled with `I`) reports world coordinates, the local electric field (`E` and `|E|`), and nearest-particle properties to help with debugging and measurement.
