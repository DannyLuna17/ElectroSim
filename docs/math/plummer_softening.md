# Plummer-like Softening

To avoid numerical instability at short range, we use a softened force law:
$
\mathbf{F}_{ij} = k\, q_i q_j\, \frac{\mathbf{r}_{ij}}{\left(\|\mathbf{r}_{ij}\|^2 + \epsilon^2\right)^{3/2}}.
$

This corresponds to a softened potential
$
\Phi(r) = -\,\frac{k\,q}{\sqrt{r^2 + \epsilon^2}},\quad \mathbf{F} = -\nabla\Phi.
$

ElectroSim uses two softening choices:
- Pairwise forces: $\epsilon = f_\mathrm{soft}(r_i + r_j)$ (contact-based).
- Field-at-point: $\epsilon_j = f_\mathrm{soft} r_j$ (source-based).

Rationale:
- Contact-based softening scales with geometric particle size to mitigate infinite forces during near-contact.
- Field visualization uses per-source radius to keep the mapping simple and stable.

Trade-offs:
- Larger $\epsilon$ increases stability but biases the force at small separations.
- Smaller $\epsilon$ increases fidelity but can require smaller `DT_S` and can cause extreme accelerations.

References: :cite:`plummer1911`.




