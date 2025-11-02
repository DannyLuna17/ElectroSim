# Physics Overview

ElectroSim models 2D Coulomb dynamics on a periodic domain with a fixed timestep integrator. This page summarises the numerical model implemented in {mod}`electrosim.simulation.physics` and how it is orchestrated by {class}`electrosim.simulation.engine.Simulation`.

## Units and Domain

- All quantities use SI units: `pos_m` in meters, `vel_mps` in m/s, `mass_kg` in kilograms, `charge_c` in Coulombs, and `radius_m` in meters.
- The simulation space is a rectangular torus of size `(WORLD_WIDTH_M, WORLD_HEIGHT_M)` derived from `PIXELS_PER_METER`. Particles that leave one edge re-enter on the opposite side.
- Distances use the minimum-image convention via {func}`electrosim.simulation.physics.minimum_image_displacement`, ensuring the shortest wrap-around separation is always chosen.
- Charges with |q| below `NEUTRAL_CHARGE_EPS` are treated as neutral for rendering and force skipping.

## Force Model

- Pairwise forces implement softened Coulomb interaction in {func}`electrosim.simulation.physics.electric_force_pair`.
- The softening radius per pair is
  $$\epsilon_{ij} = f_\text{soft} (r_i + r_j)$$
  where `f_soft = SOFTENING_FRACTION`. This keeps forces finite when particles overlap while maintaining the far-field Coulomb behaviour. See {ref}`math/plummer_softening` for derivation.
- {func}`electrosim.simulation.physics.compute_accelerations` builds the acceleration array used by the integrator. When Numba is available it JIT-compiles two kernels:
  - `_compute_accelerations_numba_parallel` (enabled when `NUMBA_PARALLEL_ACCEL = True`).
  - `_compute_accelerations_numba_serial` as the fallback serial kernel.
- Fixed, neutral, or zero-mass particles are skipped to avoid unnecessary work. If `UNIFORM_FIELD_ACTIVE` is true, the uniform field vector from `UNIFORM_FIELD_VECTOR_NC` is applied as an additional constant acceleration term.

## Time Integration Pipeline

1. {meth}`electrosim.simulation.engine.Simulation.step_frame` determines the number of substeps as `SUBSTEPS_BASE_PER_FRAME × SPEED_MULTIPLIERS[speed_index]`.
2. For each substep, {func}`electrosim.simulation.physics.rk4_integrate` advances mobile particles using classical RK4. Intermediate evaluations temporarily perturb particle state while respecting world wrapping.
3. After each RK4 stage, positions are wrapped with {func}`electrosim.simulation.physics.wrap_position_in_place` to keep them inside the torus.
4. Once all substeps are complete, the simulation updates trails, recomputes energies, and (optionally) caches forces for visualization.

The fixed timestep (`DT_S`) keeps the integrator deterministic and simplifies validation. See {ref}`math/rk4_derivation` for details.

## Collisions and Merging

- Overlap detection occurs when $\|\mathbf{r}_{ij}\| < r_i + r_j$ using the minimum-image displacement.
- Opposite-signed charges merge in an inelastic pass ({func}`electrosim.simulation.physics.resolve_collisions`). The merged particle conserves total charge and, if both were mobile, linear momentum. The new radius satisfies area conservation: $r_\text{new} = \sqrt{r_i^2 + r_j^2}$.
- Remaining overlaps (same-sign or neutral participants) go through an elastic impulse solver with restitution $e = 1$. The impulse is applied along the contact normal and positions are separated to remove penetration.
- Fixed particles behave as infinite-mass anchors during collision resolution.
- Particle `id` values are re-assigned whenever a particle is removed to keep the list contiguous.

See {ref}`math/elastic_collision_impulse` for the impulse derivation.

## Boundary Handling

- Positions are wrapped after every integration substep and post-collision via {func}`electrosim.simulation.physics.wrap_position_in_place`.
- The same minimum-image logic is reused for selection hit-testing and tooltip distance calculations within the UI layer.

## Energy Accounting

- Kinetic energy comes from {func}`electrosim.simulation.physics.total_kinetic_energy`, summing $E_k = \tfrac{1}{2} m v^2$ for mobile particles only.
- Potential energy uses {func}`electrosim.simulation.physics.total_potential_energy`:
  $$E_p = \sum_{i<j} k \frac{q_i q_j}{\max(r_{ij}, 10^{-6})}$$
  The $10^{-6}$ m clamp avoids singularities without introducing additional softening. Refer to {ref}`math/potential_energy_modeling` for the rationale.
- Energies are recomputed once per frame and exposed via the overlay as `E_kin`, `E_pot`, and `E_tot`.

## Field Evaluation and Visualization

- {func}`electrosim.simulation.physics.electric_field_at_point` computes the electric field at an arbitrary point with per-source softening $\epsilon_j = f_\text{soft} r_j$.
- {class}`electrosim.rendering.field_sampler.ElectricFieldSampler` caches these values on a regular grid when `FIELD_SAMPLER_ENABLED` is true, allowing the renderer to reuse the grid for arrow drawing.
- Display modes (`brightness` vs `length`) map field magnitude to arrow length/alpha as described in {ref}`math/field_visualization_mapping`.

## Validation Hooks

- {meth}`electrosim.simulation.engine.Simulation.start_uniform_field_validation` clears the scene and spawns the analytical uniform field scenario described in {doc}`developer_guide/validation`.
- During validation, accelerations gain a constant $(q/m)\mathbf{E}$ term and the overlay reports position/velocity error metrics each frame.
- {meth}`electrosim.simulation.engine.Simulation.stop_validation` restores configuration defaults and clears the validation state (`validation_*` fields).

## Related Modules

- {mod}`electrosim.simulation.physics` — force kernels, integration, collisions, energy bookkeeping, field sampling helpers.
- {mod}`electrosim.simulation.engine` — orchestrates simulation state, calls physics routines, manages validation.
- {mod}`electrosim.config` — authoritative constants used by the physics stack.
