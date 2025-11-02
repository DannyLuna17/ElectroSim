# ElectroSim

Welcome to the ElectroSim documentation. This site provides:
- A user guide to run and operate the simulation
- A developer guide focused on architecture, physics, and performance
- A complete API reference generated from source
- Mathematical foundations with LaTeX derivations
- Annotated, line-by-line explanations for each function

```{toctree}
:maxdepth: 2
:caption: User Guide

getting_started
user_guide/running
user_guide/controls
user_guide/visualization
user_guide/configuration
user_guide/web
```

```{toctree}
:maxdepth: 2
:caption: Developer Guide

developer_guide/architecture
developer_guide/physics_overview
developer_guide/performance
developer_guide/validation
developer_guide/web_integration
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/index
```

```{toctree}
:maxdepth: 2
:caption: Mathematical Foundations

math/coulomb_periodic
math/plummer_softening
math/rk4_derivation
math/elastic_collision_impulse
math/potential_energy_modeling
math/field_visualization_mapping
```

```{toctree}
:maxdepth: 2
:caption: Annotated Source (Line-by-line)

annotated/simulation_physics
annotated/simulation_engine
annotated/rendering_primitives
annotated/rendering_field
annotated/rendering_field_sampler
annotated/rendering_particles
annotated/rendering_trails
annotated/rendering_overlay
annotated/ui_controls
annotated/main
```