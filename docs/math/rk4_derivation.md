# RK4 Derivation

We integrate the ODE system $\dot{\mathbf{x}} = \mathbf{v}$, $\dot{\mathbf{v}} = \mathbf{a}(\mathbf{x})$ with fixed time step $\Delta t$.

Classical RK4 stages for a generic $\dot{\mathbf{y}} = \mathbf{f}(\mathbf{y})$ are:
$
\begin{aligned}
\mathbf{k}_1 &= \mathbf{f}(\mathbf{y}_n),\\
\mathbf{k}_2 &= \mathbf{f}\!\left(\mathbf{y}_n + \tfrac{\Delta t}{2}\,\mathbf{k}_1\right),\\
\mathbf{k}_3 &= \mathbf{f}\!\left(\mathbf{y}_n + \tfrac{\Delta t}{2}\,\mathbf{k}_2\right),\\
\mathbf{k}_4 &= \mathbf{f}\!\left(\mathbf{y}_n + \Delta t\,\mathbf{k}_3\right),\\
\mathbf{y}_{n+1} &= \mathbf{y}_n + \tfrac{\Delta t}{6}\left(\mathbf{k}_1 + 2\mathbf{k}_2 + 2\mathbf{k}_3 + \mathbf{k}_4\right).
\end{aligned}
$

In ElectroSim, we apply RK4 to $(\mathbf{x},\mathbf{v})$ with acceleration recomputed from temporary states. Only non-fixed particles are written back.

Error:
- Local truncation error $\mathcal{O}(\Delta t^5)$, global error $\mathcal{O}(\Delta t^4)$.
- For conservative systems, RK4 does not conserve energy exactly; small drifts can appear.

See implementation: {py:func}`electrosim.simulation.physics.rk4_integrate`.

References: :cite:`butcher_ode`.




