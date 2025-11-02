from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

import numpy as np

from electrosim.simulation.engine import Particle
try:
	# Prefer numba kernel when available
	from electrosim.simulation.physics import _compute_field_grid_numba, electric_field_at_point
	_HAS_NUMBA_FIELD = True
except Exception:
	# Graceful fallback when numba or the kernel isn't present
	from electrosim.simulation.physics import electric_field_at_point
	_HAS_NUMBA_FIELD = False
from electrosim import config as _cfg

 
@dataclass
class ElectricFieldSampler:
	"""Precompute electric field vectors on a pixel grid per frame.

	The sampler caches E vectors (shape [Hcells, Wcells, 2]) for the given grid step
	and exposes an iterator over grid centers and vectors for drawing.

	Parameters
	----------
	world_size_m : numpy.ndarray shape (2,)
		World size (m) as (Lx, Ly).
	pixels_per_meter : float
		Pixels per meter.
	grid_step_px : int
		Grid spacing in pixels between field sample points.
	softening_fraction : float
		Softening fraction used for field evaluation.
	"""
	world_size_m: np.ndarray
	pixels_per_meter: float
	grid_step_px: int
	softening_fraction: float

	# Computed buffers
	_centers_px: Optional[np.ndarray] = None
	_vectors_px: Optional[np.ndarray] = None
	_centers_m: Optional[np.ndarray] = None

	def _grid_dims(self) -> Tuple[int, int]:
		"""Return (rows, cols) of the sampling grid in cells."""
		width_px = int(round(self.world_size_m[0] * self.pixels_per_meter))
		height_px = int(round(self.world_size_m[1] * self.pixels_per_meter))
		cols = max(0, (width_px - self.grid_step_px // 2) // self.grid_step_px + 1)
		rows = max(0, (height_px - self.grid_step_px // 2) // self.grid_step_px + 1)
		return rows, cols

	def recompute(self, particles: Iterable[Particle]) -> None:
		"""Recompute field vectors over the grid for the given particle iterable.

		Packs particle data for a Numba kernel when available; falls back to
		per-point Python evaluation otherwise. Results are stored for iteration.
		"""
		rows, cols = self._grid_dims()
		if rows <= 0 or cols <= 0:
			self._centers_px = None
			self._vectors_px = None
			self._centers_m = None
			return

		centers_px = np.empty((rows, cols, 2), dtype=np.int32)
		vectors = np.zeros((rows, cols, 2), dtype=np.float32)
		centers_m = np.empty((rows * cols, 2), dtype=np.float64)

		# Fill centers and compute field
		k = 0
		for r in range(rows):
			y = self.grid_step_px // 2 + r * self.grid_step_px
			for c in range(cols):
				x = self.grid_step_px // 2 + c * self.grid_step_px
				centers_px[r, c, 0] = x
				centers_px[r, c, 1] = y
				centers_m[k, 0] = x / self.pixels_per_meter
				centers_m[k, 1] = y / self.pixels_per_meter
				k += 1

		particles_list = list(particles)
		try:
			if len(particles_list) > 0:
				N = len(particles_list)
				pos = np.empty((N, 2), dtype=np.float64)
				charge = np.empty((N,), dtype=np.float64)
				radius = np.empty((N,), dtype=np.float64)
				for i, p in enumerate(particles_list):
					pos[i, 0] = float(p.pos_m[0])
					pos[i, 1] = float(p.pos_m[1])
					charge[i] = float(p.charge_c)
					radius[i] = float(p.radius_m)
				world_size = np.array([float(self.world_size_m[0]), float(self.world_size_m[1])], dtype=np.float64)
				if _HAS_NUMBA_FIELD:
					E_flat = _compute_field_grid_numba(centers_m, pos, charge, radius, world_size, float(self.softening_fraction), float(_cfg.K_COULOMB))
				else:
					# Fallback: compute per point without numba
					E_flat = np.zeros((rows * cols, 2), dtype=np.float64)
					for k_i in range(rows * cols):
						point_m = centers_m[k_i]
						E = electric_field_at_point(point_m, particles_list, self.world_size_m, self.softening_fraction)
						E_flat[k_i, 0] = float(E[0])
						E_flat[k_i, 1] = float(E[1])
				# Reshape back to grid
				k = 0
				for r in range(rows):
					for c in range(cols):
						vectors[r, c, 0] = float(E_flat[k, 0])
						vectors[r, c, 1] = float(E_flat[k, 1])
						k += 1
			else:
				vectors[:] = 0.0
		except Exception:
			for r in range(rows):
				y = self.grid_step_px // 2 + r * self.grid_step_px
				for c in range(cols):
					x = self.grid_step_px // 2 + c * self.grid_step_px
					point_m = np.array([x / self.pixels_per_meter, y / self.pixels_per_meter], dtype=float)
					E = electric_field_at_point(point_m, particles_list, self.world_size_m, self.softening_fraction)
					vectors[r, c, 0] = float(E[0])
					vectors[r, c, 1] = float(E[1])

		self._centers_px = centers_px
		self._vectors_px = vectors
		self._centers_m = centers_m

	def iter_centers_and_vectors_px(self) -> Iterable[Tuple[Tuple[int, int], Tuple[float, float]]]:
		"""Yield `((x, y), (Ex, Ey))` pairs for each grid cell center in pixels."""
		if self._centers_px is None or self._vectors_px is None:
			return []
		rows, cols, _ = self._centers_px.shape
		out: list[Tuple[Tuple[int, int], Tuple[float, float]]] = []
		for r in range(rows):
			for c in range(cols):
				x = int(self._centers_px[r, c, 0])
				y = int(self._centers_px[r, c, 1])
				Ex = float(self._vectors_px[r, c, 0])
				Ey = float(self._vectors_px[r, c, 1])
				out.append(((x, y), (Ex, Ey)))
		return out


