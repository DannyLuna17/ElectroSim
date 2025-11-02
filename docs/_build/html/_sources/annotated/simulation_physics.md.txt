# Annotated: electrosim.simulation.physics

This page provides function-by-function, line-by-line explanations and cross-references.

## minimum_image_displacement

```python
from electrosim.config import (
    K_COULOMB,
    COLOR_POSITIVE,
    COLOR_NEGATIVE,
    COLOR_NEUTRAL,
    NEUTRAL_CHARGE_EPS,
)

def minimum_image_displacement(p_i: np.ndarray, p_j: np.ndarray, world_size_m: np.ndarray) -> np.ndarray:
    """Compute displacement from i to j using the minimum distance convention in a 2D torus."""
    delta = p_j - p_i
    for axis in (0, 1):
        L = world_size_m[axis]
        if delta[axis] > 0.5 * L:
            delta[axis] -= L
        elif delta[axis] < -0.5 * L:
            delta[axis] += L
    return delta
```

- `delta = p_j - p_i`: raw displacement before periodicity. We adopt j − i to point from i to j (consistent throughout code).
- Loop over axes applies minimum-image: if displacement exceeds half-box, wrap by one box length the other way. See {ref}`math/coulomb_periodic`.
- Returns the 2D vector with the shortest equivalent displacement on the torus.

## electric_force_pair

```python
def electric_force_pair(
    p_i: np.ndarray,
    q_i: float,
    r_i: float,
    p_j: np.ndarray,
    q_j: float,
    r_j: float,
    world_size_m: np.ndarray,
    softening_fraction: float,
) -> np.ndarray:
    r_vec = minimum_image_displacement(p_j, p_i, world_size_m)
    r2 = float(np.dot(r_vec, r_vec))
    contact = r_i + r_j
    epsilon = softening_fraction * contact
    den = (r2 + epsilon * epsilon) ** 1.5
    if den == 0.0:
        return np.zeros(2, dtype=float)
    coef = K_COULOMB * q_i * q_j / den
    return coef * r_vec
```

- Minimum-image uses `(p_j, p_i)` to point from i towards j (the force on i is along +r_vec if sign is positive). This matches the vector form of Coulomb force.
- Softening radius `epsilon` based on contact distance (see {ref}`math/plummer_softening`).
- Denominator implements $(r^2 + \epsilon^2)^{3/2}$ for the vector form $\propto \mathbf{r}/r^3$.
- Returns a 2D force vector.

## compute_accelerations (Numba path shape and algorithm)

At a high level, we pack particle arrays (structure-of-arrays) and call Numba kernels.

Key choices:
- Skip fixed, massless, and neutral particles early.
- Minimum-image per-axis inside tight loops.
- Contact-based softening.
- Multiply by inverse mass to produce accelerations.

See kernels: `_compute_accelerations_numba_serial`, `_compute_accelerations_numba_parallel`.

## total_potential_energy

```python
def total_potential_energy(particles: List["Particle"], world_size_m: np.ndarray) -> float:
    E = 0.0
    N = len(particles)
    for i in range(N):
        pi = particles[i]
        for j in range(i + 1, N):
            pj = particles[j]
            r_vec = minimum_image_displacement(pi.pos_m, pj.pos_m, world_size_m)
            r = float(np.hypot(r_vec[0], r_vec[1]))
            r_eff = max(r, 1e-6)
            if r_eff == 0.0:
                continue
            E += K_COULOMB * pi.charge_c * pj.charge_c / r_eff
    return E
```

- Pairwise sum over i<j avoids double counting.
- Distance uses minimum-image.
- `r_eff = max(r, 1e-6)` guards singularities; note the modeling choice: no softening applied here. See {ref}`math/potential_energy_modeling`.

## rk4_integrate (stages and state policy)

- Packs current positions/velocities.
- Defines helpers to temporarily set state and compute accelerations.
- Computes k1..k4 for both position and velocity components.
- Restores original state before committing final updates.
- Writes back only for non-fixed particles.

Mathematical details in {ref}`math/rk4_derivation`.

## resolve_collisions (merge and elastic phases)

- First pass: merge opposite-charge overlaps.
  - New mass `m1+m2`, charge `q1+q2`, radius `sqrt(r1^2+r2^2)`.
  - Momentum conservation if not fixed; fixed result if any fixed.
  - Update color and merge histories; wrap position; delete j; reindex ids.
- Second pass: elastic collisions for remaining overlapping pairs.
  - Compute normal, penetration correction along normal; handle fixed/infinite mass.
  - If separating, skip; else impulse with restitution e=1.

See derivation in {ref}`math/elastic_collision_impulse`.




