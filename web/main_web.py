from __future__ import annotations

import time
import asyncio

# Simple clock used only when pygame is truly unavailable
class _SimpleClock:
    def tick(self, fps: int) -> None:
        pass
    def get_fps(self) -> float:
        return 60.0

# Try to import pygame; in web we expect pygame-ce to be available
try:
    import pygame
    PYGAME_AVAILABLE = True
    print("Pygame available")
except ImportError:
    PYGAME_AVAILABLE = False
    print("Pygame not available. This build expects pygame-ce in Pyodide 0.26+")
    # Create minimal pygame-like interface for compatibility
    class FakePygame:
        class display:
            @staticmethod
            def set_mode(size): return None
            @staticmethod
            def set_caption(title): pass
            @staticmethod
            def flip(): pass
        
        class time:
            @staticmethod
            def Clock(): return _SimpleClock()
            
            @staticmethod
            def set_timer(event_id, interval): 
                # Do nothing in fallback mode
                pass
        
        class font:
            @staticmethod
            def SysFont(name, size): return None
        
        @staticmethod
        def init(): pass
        
        QUIT = 256
        USEREVENT = 256
        
        class event:
            @staticmethod
            def get(): return []
    
    pygame = FakePygame()

# Import configuration first
config = None
try:
    # Use web-compatible config
    import config_web as config
    print("Config loaded successfully")
except ImportError as e:
    print(f"Config import error: {e}")
    # Create a minimal config fallback
    class MinimalConfig:
        PIXELS_PER_METER = 80
        WINDOW_WIDTH_PX = 1280
        WINDOW_HEIGHT_PX = 800
        FPS_TARGET = 30
        COLOR_BG = (20, 20, 20)
        FIELD_GRID_STEP_PX = 30
        FIELD_VIS_MODE = "brightness"
        SOFTENING_FRACTION = 0.1
        PROFILE_OVERLAY_ENABLED = True
        WEB_MODE = True
    config = MinimalConfig()
    print("Using minimal config fallback")

# Import the ElectroSim modules
Simulation = None
try:
    from electrosim.simulation.engine import Simulation
    print("Simulation engine loaded")
except ImportError as e:
    print(f"Simulation import error: {e}")
    print("Creating minimal simulation fallback...")
    
    # Create a minimal simulation class for testing
    class MinimalSimulation:
        def __init__(self):
            self.particles = []
            self.world_size_m = (16.0, 10.0)
            self.show_meter_grid = False
            self.show_field = False
            self.show_trails = False
            self.show_velocities = False
            self.show_forces = False
            self.selected_index = -1
            self.speed_index = 1
            self.energy_kin = 0.0
            self.energy_pot = 0.0
            self.energy_tot = 0.0
            self.last_forces = []
            print("Minimal simulation created")
        
        def step_frame(self):
            # Do nothing for now
            pass
    
    Simulation = MinimalSimulation

RENDERING_AVAILABLE = False

# Only import rendering modules if pygame is available
if PYGAME_AVAILABLE:
    try:
        from electrosim.rendering.draw import (
            draw_field_grid,
            draw_meter_grid,
            draw_force_vectors,
            draw_overlay,
            draw_particle_glows,
            draw_particles,
            draw_trails,
            draw_velocity_vectors,
        )
        from electrosim.ui.controls import InputState, handle_events, render_placement_preview, render_hover_tooltip
        from electrosim.rendering.trails import draw_polyline_world
        RENDERING_AVAILABLE = True
        print("Rendering modules loaded")
    except Exception as e:
        # Rendering stack depends on accelerated kernels; degrade gracefully
        print(f"Rendering import error: {e}, using dummy functions")
        RENDERING_AVAILABLE = False

if not RENDERING_AVAILABLE:
    # Create dummy classes for when pygame is not available
    class InputState:
        def __init__(self): pass
    
    # Dummy render functions
    def handle_events(*args): pass
    def draw_field_grid(*args): pass
    def draw_meter_grid(*args): pass
    def draw_force_vectors(*args): pass
    def draw_overlay(*args): pass
    def draw_particle_glows(*args): pass
    def draw_particles(*args): pass
    def draw_trails(*args): pass
    def draw_velocity_vectors(*args): pass
    def render_placement_preview(*args): pass
    def render_hover_tooltip(*args): pass
    def draw_polyline_world(*args): pass
    print("Dummy rendering functions created")


class WebSimulation:
    """Web-adapted version of the ElectroSim simulation."""
    
    def __init__(self):
        self.running = False
        self.screen = None
        self.clock = None
        self.font = None
        self.sim = None
        self.input_state = None
        self.ppm = config.PIXELS_PER_METER
        self.last_frame_time = 0
        self.time = 0.0
        
    def initialize(self):
        """Initialize pygame and simulation components."""
        try:
            if PYGAME_AVAILABLE:
                # Initialize only subsystems we need in the web (avoid audio)
                if hasattr(pygame, 'display'):
                    # Ensure SDL is targeting our canvas
                    try:
                        import os
                        if not os.environ.get("SDL_HINT_EMSCRIPTEN_KEYBOARD_ELEMENT"):
                            os.environ["SDL_HINT_EMSCRIPTEN_KEYBOARD_ELEMENT"] = "#canvas"
                    except Exception:
                        pass
                    pygame.display.init()
                if hasattr(pygame, 'font'):
                    pygame.font.init()
                # Initialize display - in web this will be handled by the browser
                self.screen = pygame.display.set_mode((config.WINDOW_WIDTH_PX, config.WINDOW_HEIGHT_PX))
                pygame.display.set_caption("ElectroSim - Web Version")
                self.clock = pygame.time.Clock()
                try:
                    self.font = pygame.font.Font(None, 16)
                except Exception:
                    # Fallback to sysfont if default font fails
                    self.font = pygame.font.SysFont("sans-serif", 16)
            else:
                # Fallback mode without pygame
                self.screen = None
                self.clock = FakeClock()
                self.font = None
                print("Running in fallback mode without pygame")
            
            # Initialize simulation
            self.sim = Simulation()
            self.input_state = InputState()
            
            print("ElectroSim initialized successfully!")
            return True
            
        except Exception as e:
            print(f"Failed to initialize simulation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_frame(self):
        """Process one frame of the simulation."""
        if not self.running:
            return
            
        try:
            frame_t0 = time.perf_counter()
            
            # Handle events and controls - skip if pygame not available
            if PYGAME_AVAILABLE:
                handle_events(pygame, self.sim, self.input_state, self.ppm)
            
            # Physics step
            t_ph0 = time.perf_counter()
            self.sim.step_frame()
            t_ph1 = time.perf_counter()
            physics_ms = (t_ph1 - t_ph0) * 1000.0
            
            # Rendering - only if pygame and rendering stack are available
            field_ms = 0.0
            t_draw0 = time.perf_counter()
            
            if PYGAME_AVAILABLE and RENDERING_AVAILABLE and self.screen:
                self.screen.fill(config.COLOR_BG)
                
                # Draw meter grid if enabled
                if self.sim.show_meter_grid:
                    draw_meter_grid(self.screen, self.sim.world_size_m, self.ppm)
                
                # Draw electric field if enabled
                if self.sim.show_field or getattr(self.sim, "validation_active", False) or getattr(config, "UNIFORM_FIELD_VISUAL_OVERRIDE", False):
                    FIELD_GRID_STEP_PX = config.FIELD_GRID_STEP_PX
                    if config.FIELD_VIS_MODE != "brightness":
                        FIELD_GRID_STEP_PX = int(config.FIELD_GRID_STEP_PX * 2.6) 
                    t_f0 = time.perf_counter()
                    draw_field_grid(self.screen, self.sim.particles, self.sim.world_size_m, self.ppm, FIELD_GRID_STEP_PX, config.SOFTENING_FRACTION)
                    t_f1 = time.perf_counter()
                    field_ms += (t_f1 - t_f0) * 1000.0
                
                # Draw particle glows
                draw_particle_glows(self.screen, self.sim.particles, self.ppm)
                
                # Draw trails if enabled
                if self.sim.show_trails:
                    draw_trails(self.screen, self.sim.particles, self.ppm)
                
                # Draw theoretical trajectory if validation is active
                if getattr(self.sim, "validation_active", False) and self.sim.validation_theory_traj:
                    points = [xy for (_, xy) in self.sim.validation_theory_traj]
                    draw_polyline_world(self.screen, points, config.COLOR_THEORY_TRAJECTORY, 2, self.ppm)
                
                # Draw particles
                draw_particles(self.screen, self.sim.particles, self.ppm, self.sim.selected_index)
                
                # Draw velocity vectors if enabled
                if self.sim.show_velocities:
                    draw_velocity_vectors(self.screen, self.sim.particles, self.ppm)
                
                # Draw force vectors if enabled
                if self.sim.show_forces:
                    draw_force_vectors(self.screen, self.sim.particles, self.sim.last_forces, self.ppm)
                
                # Draw placement preview
                render_placement_preview(self.screen, self.input_state, self.ppm)
                
            t_draw1 = time.perf_counter()
            draw_ms_total = (t_draw1 - t_draw0) * 1000.0
            draw_ms = max(0.0, draw_ms_total - field_ms)
            
            # Draw overlay with stats
            fps = self.clock.get_fps() or float(config.FPS_TARGET)
            speed_label = {0: "0.5×", 1: "1×", 2: "2×", 3: "4×"}[self.sim.speed_index]
            sim_state = {
                "fps": fps,
                "n": len(self.sim.particles),
                "speed_label": speed_label,
                "dt_s": config.DT_S,
                "substeps": max(1, int(config.SUBSTEPS_BASE_PER_FRAME * config.SPEED_MULTIPLIERS[self.sim.speed_index])),
                "E_kin": self.sim.energy_kin,
                "E_pot": self.sim.energy_pot,
                "E_tot": self.sim.energy_tot,
            }
            
            # Validation overlay if active
            if getattr(self.sim, "validation_active", False):
                E = (float(config.UNIFORM_FIELD_VECTOR_NC[0]), float(config.UNIFORM_FIELD_VECTOR_NC[1]))
                if getattr(self.sim, "validation_accel_mps2", None) is not None:
                    a = (float(self.sim.validation_accel_mps2[0]), float(self.sim.validation_accel_mps2[1]))
                else:
                    a = (0.0, 0.0)
                cur = getattr(self.sim, "validation_current_errors", {}) or {}
                val_payload = {
                    "active": True,
                    "E": E,
                    "a": a,
                    "t": float(cur.get("t", 0.0)),
                    "pos_err": float(cur.get("pos_err", 0.0)),
                    "vel_err": float(cur.get("vel_err", 0.0)),
                    "dt_s": float(config.DT_S),
                    "duration_s": float(getattr(config, "VALIDATION_DURATION_S", 0.0)),
                }
                val_payload["reached_end"] = bool(getattr(self.sim, "validation_reached_end", False))
                pos_th = getattr(self.sim, "validation_final_theory_pos_m", None)
                vel_th = getattr(self.sim, "validation_final_theory_vel_mps", None)
                pos_sim = getattr(self.sim, "validation_final_sim_pos_m", None)
                vel_sim = getattr(self.sim, "validation_final_sim_vel_mps", None)
                if pos_th is not None and vel_th is not None:
                    val_payload["pos_th"] = (float(pos_th[0]), float(pos_th[1]))
                    val_payload["vel_th"] = (float(vel_th[0]), float(vel_th[1]))
                if pos_sim is not None and vel_sim is not None:
                    val_payload["pos_sim"] = (float(pos_sim[0]), float(pos_sim[1]))
                    val_payload["vel_sim"] = (float(vel_sim[0]), float(vel_sim[1]))
                sim_state["validation"] = val_payload
            
            # Performance overlay if enabled
            if getattr(config, "PROFILE_OVERLAY_ENABLED", False):
                tot_ms = (time.perf_counter() - frame_t0) * 1000.0
                sim_state["profile"] = {
                    "physics_ms": float(physics_ms),
                    "field_ms": float(field_ms),
                    "draw_ms": float(draw_ms),
                    "total_ms": float(tot_ms),
                }
            
            if PYGAME_AVAILABLE and RENDERING_AVAILABLE and self.screen:
                draw_overlay(self.screen, self.font, sim_state, self.input_state.overlay_enabled)
                render_hover_tooltip(self.screen, self.font, self.sim, self.input_state, self.ppm)
                
                # Update display
                pygame.display.flip()
            else:
                # In fallback mode, just print simulation state occasionally
                if int(self.time * 10) % 60 == 0:  # Every 6 seconds
                    print(f"Simulation running: {len(self.sim.particles)} particles, t={self.time:.1f}s")
            
            self.clock.tick(config.FPS_TARGET)
            self.time = time.perf_counter() - frame_t0
            
        except Exception as e:
            print(f"Error in frame handling: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """Start the simulation."""
        if not self.initialize():
            return False
        
        self.running = True
        print("ElectroSim web simulation started!")
        return True
    
    def stop(self):
        """Stop the simulation."""
        self.running = False
        print("ElectroSim web simulation stopped!")


# Global simulation instance
web_sim = None


def start_web_simulation():
    """Start the web version of ElectroSim."""
    global web_sim
    
    try:
        web_sim = WebSimulation()
        if web_sim.start():
            # Start the main loop
            run_simulation_loop()
        else:
            print("Failed to start simulation")
    except Exception as e:
        print(f"Error starting web simulation: {e}")
        import traceback
        traceback.print_exc()


def run_simulation_loop():
    """Run the main simulation loop for web."""
    global web_sim
    
    if not web_sim:
        print("No simulation instance available")
        return
    
    print("Starting simulation loop...")
    
    if PYGAME_AVAILABLE:
        # Simple loop without using set_timer (not implemented on WASM)
        running = True
        while running and web_sim and web_sim.running:
            web_sim.handle_frame()
            # Let the browser breathe a bit
            # time.sleep(1.0 / max(1, int(config.FPS_TARGET)))
    else:
        # Fallback mode - simple loop
        print("Running in simplified loop mode...")
        frame_count = 0
        start_time = time.perf_counter()
        
        while web_sim and web_sim.running:
            try:
                web_sim.handle_frame()
                frame_count += 1
                
                # Print status every few seconds
                if frame_count % 180 == 0:  
                    elapsed = time.perf_counter() - start_time
                    print(f"Simulation running: {frame_count} frames, {elapsed:.1f}s elapsed")
                
            except KeyboardInterrupt:
                print("Simulation interrupted")
                break
            except Exception as e:
                print(f"Error in simulation loop: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print("Simulation loop ended")

# Async variants for Pyodide so we don't block the browser main thread
async def start_web_simulation_async() -> None:
    global web_sim
    try:
        web_sim = WebSimulation()
        if web_sim.start():
            await run_simulation_loop_async()
        else:
            print("Failed to start simulation")
    except Exception as e:
        print(f"Error starting web simulation (async): {e}")
        import traceback
        traceback.print_exc()


async def run_simulation_loop_async() -> None:
    global web_sim
    if not web_sim:
        print("No simulation instance available")
        return
    print("Starting simulation loop (async)...")
    while web_sim and web_sim.running:
        web_sim.handle_frame()
        # Yield to browser event loop
        await asyncio.sleep(0)

def stop_web_simulation():
    """Stop the web simulation."""
    global web_sim
    if web_sim:
        web_sim.stop()


if __name__ == "__main__":
    start_web_simulation()
