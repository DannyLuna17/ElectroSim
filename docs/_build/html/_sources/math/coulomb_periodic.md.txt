# Coulomb Force with Periodic Boundary Conditions

We consider a 2D torus domain with size $(L_x, L_y)$. The minimum-image displacement between points $\mathbf{p}_i$ and $\mathbf{p}_j$ is computed per-axis:
$
\Delta x = (x_j - x_i) - L_x \cdot \operatorname{round}\!\left(\frac{x_j - x_i}{L_x}\right),\quad
\Delta y = (y_j - y_i) - L_y \cdot \operatorname{round}\!\left(\frac{y_j - y_i}{L_y}\right).
$

Electrostatic force with Plummer-like softening is
$
\mathbf{F}_{ij} = k\, q_i q_j \frac{\boldsymbol{\Delta r}}{\left(\|\boldsymbol{\Delta r}\|^2 + \epsilon^2\right)^{3/2}},
$
where $\epsilon$ is discussed in {ref}`math/plummer_softening`.

Connections:
- Implementation: {py:func}`electrosim.simulation.physics.minimum_image_displacement` and {py:func}`electrosim.simulation.physics.electric_force_pair`.
- Used by: accelerations, field evaluation, selection, collisions.

References: :cite:`griffiths_electrodynamics`, :cite:`hockney_eastwood`.




