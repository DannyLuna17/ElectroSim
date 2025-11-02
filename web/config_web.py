# Web-compatible configuration for ElectroSim
# This overrides certain settings for better web performance

# Disable Numba for web compatibility
import os
os.environ['NUMBA_DISABLE_JIT'] = '1'

# Import the original config
from electrosim.config import *

WINDOW_WIDTH_PX: int = 1100
WINDOW_HEIGHT_PX: int = 480

# Override performance settings for web
PROFILE_OVERLAY_ENABLED = True  # Show performance stats in web
FIELD_SAMPLER_ENABLED = True # Disable for better performance in browser
FPS_TARGET = 60

# Web-specific settings
WEB_MODE = True

