from __future__ import annotations

"""Global configuration constants (window, physics, visuals, UI)."""

# Window
WINDOW_WIDTH_PX: int = 1280
WINDOW_HEIGHT_PX: int = 800
FPS_TARGET: int = 60

# World (m) and scale
PIXELS_PER_METER: float = 80.0  # 1 m = 80 px
WORLD_WIDTH_M: float = WINDOW_WIDTH_PX / PIXELS_PER_METER  # 16.0 m
WORLD_HEIGHT_M: float = WINDOW_HEIGHT_PX / PIXELS_PER_METER  # 10.0 m

# Physics 
K_COULOMB: float = 8.9875517873681764e9  # N·m^2/C^2
DT_S: float = 0.001  # s (fixed timestep)
# Base integrator substeps per frame at 1x speed
SUBSTEPS_BASE_PER_FRAME: int = 8
SPEED_MULTIPLIERS: tuple[float, ...] = (0.5, 1.0, 2.0, 4.0)
# Softening as a fraction of contact radius (r_i + r_j)
SOFTENING_FRACTION: float = 0.1

# Particles
MAX_PARTICLES: int = 100
DEFAULT_CHARGE_C: float = 5e-6  # +5 microC
DEFAULT_MASS_KG: float = 0.02
# Choose a default radius within [MIN_RADIUS_M, MAX_RADIUS_M]
DEFAULT_RADIUS_M: float = 0.1
MIN_CHARGE_C: float = -100e-6
MAX_CHARGE_C: float = 100e-6
MIN_MASS_KG: float = 0.005
MAX_MASS_KG: float = 0.2
MIN_RADIUS_M: float = 0.02
MAX_RADIUS_M: float = 0.15

# Editing step sizes
CHARGE_STEP_C: float = 1e-6
MASS_STEP_KG: float = 0.005
RADIUS_STEP_M: float = 0.005

# Visualization
COLOR_BG: tuple[int, int, int] = (18, 18, 22)
COLOR_GRID: tuple[int, int, int] = (35, 35, 40)
COLOR_POSITIVE: tuple[int, int, int] = (255, 85, 85)
COLOR_NEGATIVE: tuple[int, int, int] = (75, 139, 255)
COLOR_NEUTRAL: tuple[int, int, int] = (255, 255, 255)
COLOR_FIXED_BORDER: tuple[int, int, int] = (230, 200, 80)
COLOR_SELECTED_BORDER: tuple[int, int, int] = (255, 255, 255)
COLOR_FORCE_VECTOR: tuple[int, int, int] = (255, 225, 100)
COLOR_VELOCITY_VECTOR: tuple[int, int, int] = (120, 255, 120)
COLOR_FIELD_VECTOR: tuple[int, int, int] = (30, 200, 60)
COLOR_TRAIL_POS: tuple[int, int, int] = (255, 120, 120)
COLOR_TRAIL_NEG: tuple[int, int, int] = (120, 160, 255)

# Glow effect
GLOW_ENABLED: bool = True
GLOW_ALPHA_AT_MAX: int = 255  # alpha when |q| = MAX_CHARGE_C
GLOW_RADIUS_SCALE: float = 100.0

# Electric field, two display modes
# "brightness": fixed-length arrows with brightness/alpha based on |E|
# "length": arrows with variable length
FIELD_VIS_MODE: str = "brightness"
FIELD_FIXED_ARROW_LENGTH_PX: float = 16.0
FIELD_BRIGHTNESS_SCALE: float = 2.0
FIELD_ALPHA_MIN_DRAW: int = 2

FIELD_GRID_STEP_PX: int = 30
FIELD_VECTOR_MAX_LENGTH_PX: float = 50.0
# Converts |E| to pixels for arrow drawing
FIELD_VECTOR_SCALE: float = 2e-3

# Performance
FIELD_SAMPLER_ENABLED: bool = True  # cache field grid per frame
NUMBA_PARALLEL_ACCEL: bool = True   # use prange parallel loop if available
NUMBA_FASTMATH: bool = False        # allow fastmath in numba kernels (accuracy tradeoff)
PROFILE_OVERLAY_ENABLED: bool = True  # show per-frame timings in overlay

# Glow cache (rendering)
GLOW_CACHE_INTENSITY_STEPS: int = 1
GLOW_CACHE_MAX_SURFACES: int = 12000000

# Metric grid (meters)
COLOR_GRID_MAJOR: tuple[int, int, int] = (60, 60, 70)
GRID_METER_STEP: float = 1.0  # 1 m between lines
GRID_MAJOR_EVERY: int = 1     # major line every 1 m
GRID_LINE_WIDTH: int = 1
GRID_MAJOR_LINE_WIDTH: int = 2

FORCE_VECTOR_SCALE: float = 100.0  # px per Newton (clamped internally)
VELOCITY_VECTOR_SCALE: float = 10.0  # px per (m/s)
VECTOR_MAX_LENGTH_PX: float = 80.0

TRAJECTORY_HISTORY_SECONDS: float = 3.0

# Trajectories (appearance)
TRAIL_WIDTH_PX: int = 3
TRAIL_ALPHA_MAX: int = 235
TRAIL_MIN_ALPHA: int = 5
TRAIL_FADE_SECONDS: float = TRAJECTORY_HISTORY_SECONDS
TRAIL_AA_EDGE_EXTEND_PX: int = 1
TRAIL_AA_EDGE_OPACITY_FACTOR: float = 0.35

# Interaction
VELOCITY_PER_PIXEL: float = 0.2  # 1 px drag = 0.2 m/s
VELOCITY_MAX_MPS: float = 10.0

# Threshold to consider a particle neutral when coloring (prevents flicker due to rounding)
NEUTRAL_CHARGE_EPS: float = 1e-12

# Overlay
OVERLAY_TEXT_COLOR: tuple[int, int, int] = (230, 230, 230)
OVERLAY_SHADOW_COLOR: tuple[int, int, int] = (0, 0, 0)
OVERLAY_SHADOW_OFFSET: tuple[int, int] = (1, 1)


# Uniform field validation
# When active, simulation adds uniform E to accelerations and field grid can show only this uniform field
UNIFORM_FIELD_ACTIVE: bool = False
# Constant electric field vector (N/C) used during validation
UNIFORM_FIELD_VECTOR_NC: tuple[float, float] = (500.0, 0.0)
# When True, field visualization renders ONLY the uniform field (ignores particle contributions)
UNIFORM_FIELD_VISUAL_OVERRIDE: bool = False

# Validation scenario parameters
VALIDATION_DURATION_S: float = 10.0

# Visualization color for theoretical trajectory overlay
COLOR_THEORY_TRAJECTORY: tuple[int, int, int] = (230, 230, 80)
