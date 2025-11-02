# Annotated: electrosim.rendering.particles

## draw_particles
- Circle fill of particle radius in pixels; border for fixed/selected using configured colors.

## draw_velocity_vectors
- Scales velocity by `VELOCITY_VECTOR_SCALE` and clamps at `VECTOR_MAX_LENGTH_PX`.

## draw_force_vectors
- Uses `Simulation.last_forces` if available; scales by `FORCE_VECTOR_SCALE`.

## draw_particle_glows
- Skips neutral within `NEUTRAL_CHARGE_EPS`.
- Intensity proportional to |q| / `MAX_CHARGE_C`.




