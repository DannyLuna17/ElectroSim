# Elastic Collision Impulse

Given two discs with masses $m_1, m_2$, velocities $\mathbf{v}_1, \mathbf{v}_2$, and unit normal $\mathbf{n}$ from 1 to 2 at contact, the normal relative speed is $v_{rel,n} = (\mathbf{v}_2 - \mathbf{v}_1)\cdot\mathbf{n}$.

With restitution $e$, the scalar impulse is
$
 j = -\frac{(1+e)\, v_{rel,n}}{1/m_1 + 1/m_2}.
$

Velocity updates:
$
\mathbf{v}_1' = \mathbf{v}_1 - \frac{j}{m_1} \mathbf{n},\qquad
\mathbf{v}_2' = \mathbf{v}_2 + \frac{j}{m_2} \mathbf{n}.
$

ElectroSim uses $e=1$ (perfectly elastic). Fixed particles are treated as $m=\infty$ so the corresponding inverse mass is zero.

Penetration correction displaces positions along $\mathbf{n}$ proportionally to masses (or entirely on the mobile body if the other is fixed).

See implementation: {py:func}`electrosim.simulation.physics.resolve_collisions`.

References: :cite:`baraff_rigid_body`.




