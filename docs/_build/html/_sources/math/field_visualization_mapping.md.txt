# Field Visualization Mapping

Let $\mathbf{E}(\mathbf{x})$ be the electric field. We map it to pixel arrows as follows:

## Brightness mode
- Arrow length is fixed: `FIELD_FIXED_ARROW_LENGTH_PX`.
- Alpha/brightness scales with magnitude: $t = \mathrm{clamp}\big( s\,\|\mathbf{E}\| / L_{max} \big)$ where `s = FIELD_BRIGHTNESS_SCALE`, `L_{max} = FIELD_VECTOR_MAX_LENGTH_PX`.
- Color blends toward white as magnitude grows to enhance visibility.

## Length mode
- Arrow length scales with magnitude: $\ell = \mathrm{clamp}( \alpha \\|\mathbf{E}\\|, L_{max})$ with `\alpha = FIELD_VECTOR_SCALE` and clamp `L_{max} = FIELD_VECTOR_MAX_LENGTH_PX`.

Implementation: {py:func}`electrosim.rendering.field.draw_field_grid` and {py:class}`electrosim.rendering.field_sampler.ElectricFieldSampler`.




