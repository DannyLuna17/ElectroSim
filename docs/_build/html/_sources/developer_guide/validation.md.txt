# Validation

ElectroSim ships with an interactive validation harness that compares the
numerical integrator against the analytical solution for a particle in a
uniform electric field. Use it to confirm that physics changes or performance
optimisations have not introduced regressions.

## Uniform Field Scenario

The built-in scenario accelerates a single charged particle with a constant
field vector configured via `UNIFORM_FIELD_VECTOR_NC` in
`electrosim/config.py`. When active, the simulation:

- Clears the scene and spawns one particle at world centre with
  `DEFAULT_CHARGE_C`, `DEFAULT_MASS_KG`, and `DEFAULT_RADIUS_M`.
- Enables the uniform field contribution for both forces and field
  visualisation via `UNIFORM_FIELD_ACTIVE = True` and
  `UNIFORM_FIELD_VISUAL_OVERRIDE = True`.
- Tracks the analytical trajectory $x(t) = x_0 + v_0 t + \tfrac{1}{2} a t^2$
  where $a = (q/m)E$ for comparison against the numerically integrated state.
- Samples the theoretical path at the display cadence (1/`FPS_TARGET`) so it
  can be drawn as a yellow guideline (`COLOR_THEORY_TRAJECTORY`).

The default duration is `VALIDATION_DURATION_S = 10.0`. After reaching the end
time, the simulation auto-pauses and prints a summary of the final position and
velocity error to stdout for easy logging.

## How to Run It

1. Launch the desktop build: `python main.py`.
2. Press `U` (see `docs/user_guide/controls.md`). The current scene is replaced
   with the uniform-field setup and validation begins immediately.
3. Observe the overlay and trajectory while the timer counts up to
   `VALIDATION_DURATION_S`.
4. Inspect the console output when the run completes. The final state is kept
   on screen so you can inspect the particle visually.

To exit validation mode, either press `R` to reset to the default scene,
`C` to clear all particles, or simply close the window. Calling
`Simulation.stop_validation()` from code also restores configuration defaults
(`UNIFORM_FIELD_ACTIVE = False`, `UNIFORM_FIELD_VISUAL_OVERRIDE = False`).

## Reading the Overlay

While validation is active, the overlay (rendered by
{mod}`electrosim.rendering.overlay`) displays an additional section:

- **E**: The configured uniform field vector in N/C.
- **a**: Acceleration derived from $(q/m)E$ using the active particle mass and
  charge.
- **t** and **dt**: Current validation time and integrator step.
- **|pos_err|** and **|vel_err|**: Euclidean error between analytical and
  simulated position/velocity with periodic wrapping applied.
- Final theoretical vs simulated position/velocity once
  `VALIDATION_DURATION_S` has elapsed.

The yellow line rendered in `main.py` uses `validation_theory_traj` to plot the
analytical solution. This makes divergence visually obvious even before the
numeric error grows large.

## Customising the Scenario

All relevant knobs live in `electrosim/config.py`:

- `UNIFORM_FIELD_VECTOR_NC`: Change the acceleration direction/magnitude.
- `DEFAULT_CHARGE_C`, `DEFAULT_MASS_KG`: Alter particle properties to stress
  different regimes.
- `VALIDATION_DURATION_S`: Adjust the run length. Longer runs reveal accumulated
  integration error but increase execution time.
- `FPS_TARGET` and `SUBSTEPS_BASE_PER_FRAME`: Increase to reduce local truncation
  error at the cost of runtime.

Because the harness operates on the full simulation stack, you can experiment
with alternative integrators or force kernels simply by modifying the regular
code paths. The validation overlay will pick up the results automatically via
the `Simulation.validation_*` fields.

## Automating from Code

If you need to trigger validation from tests or scripts, import the simulation
engine and call {meth}`electrosim.simulation.engine.Simulation.start_uniform_field_validation`.
During the run, increment frames as usual with {meth}`Simulation.step_frame`.
After completion, inspect `validation_current_errors` or the stored final
vectors (`validation_final_theory_pos_m`, `validation_final_sim_pos_m`, etc.)
for assertions. Remember to call {meth}`Simulation.stop_validation` to reset the
global config flags when you are done.

