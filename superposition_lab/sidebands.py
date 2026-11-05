"""Synthetic electron energy-sideband control experiment.

This models a truncated ladder of energy sidebands separated by one photon
energy. It tests whether phase noise affects coherent population
redistribution. It is not a free-electron hardware model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import numpy as np


@dataclass(frozen=True)
class SidebandConfig:
    """Parameters for a truncated energy-sideband simulation."""

    levels: int = 16
    central_level: int = 8
    coupling: float = 1.0
    phase_noise: float = 0.0
    dt: float = 0.10
    steps: int = 50
    seed: int = 17

    def __post_init__(self):
        if self.levels < 3 or self.levels > 64:
            raise ValueError("levels must be between 3 and 64")
        if not 0 <= self.central_level < self.levels:
            raise ValueError("central_level must be a valid level")
        if self.coupling < 0 or self.phase_noise < 0:
            raise ValueError("coupling and phase_noise must be nonnegative")
        if self.dt <= 0 or self.steps < 1:
            raise ValueError("dt must be positive and steps must be at least 1")


def ladder_hamiltonian(levels):
    """Return the diagonal energy Hamiltonian for a truncated sideband ladder."""
    return np.diag(np.arange(levels, dtype=float) - (levels - 1) / 2.0)


def modulation_hamiltonian(levels, central, coupling):
    """Return nearest-neighbour sideband coupling centred on the ladder."""
    h = np.zeros((levels, levels), dtype=np.complex128)
    for n in range(levels - 1):
        h[n, n + 1] = coupling
        h[n + 1, n] = coupling
    return h


def apply_phase_noise(rho, sigma, rng):
    """Apply random diagonal phase noise in the energy basis."""
    if sigma < 0:
        raise ValueError("phase_noise must be nonnegative")
    phases = rng.normal(0.0, sigma, size=rho.shape[0])
    u = np.diag(np.exp(1j * phases))
    return u @ rho @ u.conj().T


def run_sideband_experiment(config=None):
    """Run a coherent modulation experiment on a truncated sideband ladder."""
    cfg = config or SidebandConfig()
    rng = np.random.default_rng(cfg.seed)
    energy_h = ladder_hamiltonian(cfg.levels)
    drive_h = modulation_hamiltonian(cfg.levels, cfg.central_level, cfg.coupling)

    psi = np.zeros(cfg.levels, dtype=np.complex128)
    psi[cfg.central_level] = 1.0
    rho = np.outer(psi, psi.conj())

    vals, vecs = np.linalg.eigh(energy_h + drive_h)
    u = (vecs * np.exp(-1j * vals * cfg.dt)) @ vecs.conj().T

    history = []
    for step in range(cfg.steps + 1):
        history.append({
            "step": step,
            "time": step * cfg.dt,
            "central_population": float(np.real(rho[cfg.central_level, cfg.central_level])),
            "purity": float(np.real(np.trace(rho @ rho))),
            "mean_abs_sideband": float(np.mean(np.abs(rho[~np.eye(cfg.levels, dtype=bool)]))),
        })
        if step == cfg.steps:
            break
        rho = u @ rho @ u.conj().T
        rho = apply_phase_noise(rho, cfg.phase_noise * np.sqrt(cfg.dt), rng)
        rho = 0.5 * (rho + rho.conj().T)
        rho /= np.trace(rho).real

    return {
        "status": "SYNTHETIC_CLASSICAL_SIMULATION",
        "model": "truncated_energy_sideband_ladder",
        "config": asdict(cfg),
        "history": history,
    }


if __name__ == "__main__":
    print(json.dumps(run_sideband_experiment(), indent=2))
