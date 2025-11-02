# Potential Energy Modeling

We report electrostatic potential energy as
$
E_p = \sum_{i<j} k \frac{q_i q_j}{\max(r_{ij}, 10^{-6})}.
$

Notes:
- We do not apply softening to $E_p$; instead, a singularity guard avoids division by zero.
- This choice makes $E_p$ not exactly consistent with the softened forces used in dynamics, but remains a useful qualitative indicator.
- Merges of opposite charges are inelastic; energy is not conserved across merges by design.

See computation: {py:func}`electrosim.simulation.physics.total_potential_energy`.




