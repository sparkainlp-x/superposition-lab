"""Coherent excitation transport on a 3x3 synthetic lattice.

The state is one excitation coherently distributed across nine sites. This
is a tight-binding transport model, not nine independent density matrices.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import numpy as np


@dataclass(frozen=True)
class TransportConfig:
    """Parameters for a 3x3 coherent-transport experiment."""

    coupling: float = 0.10
    disorder: float = 0.20
    dephasing: float = 0.05
    dt: float = 0.05
    steps: int = 200
    source: tuple = (0, 0)
    target: tuple = (2, 2)
    seed: int = 42

    def __post_init__(self):
        if self.coupling < 0 or self.disorder < 0 or self.dephasing < 0:
            raise ValueError("coupling, disorder and dephasing must be nonnegative")
        if self.dt <= 0 or self.steps < 1:
            raise ValueError("dt must be positive and steps must be at least 1")
        if not all(0 <= v < 3 for v in (*self.source, *self.target)):
            raise ValueError("source and target must be valid 3x3 coordinates")


def site_index(i, j):
    """Map a 3x3 coordinate to a flat site index."""
    return 3 * i + j


def build_hamiltonian(config, rng):
    """Build a nearest-neighbour Hamiltonian with diagonal disorder."""
    n = 9
    h = np.zeros((n, n), dtype=np.complex128)
    for i in range(3):
        for j in range(3):
            h[site_index(i, j), site_index(i, j)] = rng.normal(0.0, config.disorder)

    neighbours = []
    for i in range(3):
        for j in range(3):
            if j + 1 < 3:
                neighbours.append(((i, j), (i, j + 1)))
            if i + 1 < 3:
                neighbours.append(((i, j), (i + 1, j)))

    for (a, b), (c, d) in neighbours:
        ia, ib = site_index(a, b), site_index(c, d)
        phase = rng.uniform(0.0, 2.0 * np.pi)
        value = config.coupling * np.exp(1j * phase)
        h[ia, ib] = value
        h[ib, ia] = value.conj()
    return h


def apply_dephasing(rho, gamma):
    """Apply dephasing in the site basis while preserving populations."""
    if gamma < 0:
        raise ValueError("dephasing must be nonnegative")
    factors = np.exp(-gamma * np.abs(np.subtract.outer(np.arange(9), np.arange(9))))
    out = rho * factors
    return 0.5 * (out + out.conj().T)


def evolve(config, hamiltonian, rho0):
    """Evolve a density matrix using exact unitary steps and site dephasing."""
    vals, vecs = np.linalg.eigh(hamiltonian)
    u = (vecs * np.exp(-1j * vals * config.dt)) @ vecs.conj().T
    rho = rho0.copy()
    history = []

    for step in range(config.steps + 1):
        target = site_index(*config.target)
        history.append({
            "step": step,
            "time": step * config.dt,
            "target_population": float(np.real(rho[target, target])),
            "purity": float(np.real(np.trace(rho @ rho))),
            "mean_offdiagonal": float(np.mean(np.abs(rho[~np.eye(9, dtype=bool)]))),
        })
        if step == config.steps:
            break
        rho = u @ rho @ u.conj().T
        rho = apply_dephasing(rho, config.dephasing * config.dt)
        rho = 0.5 * (rho + rho.conj().T)
        rho /= np.trace(rho).real

    return history


def run_transport_experiment(config=None):
    """Run one seeded transport simulation and return its trajectory."""
    cfg = config or TransportConfig()
    rng = np.random.default_rng(cfg.seed)
    h = build_hamiltonian(cfg, rng)
    source = site_index(*cfg.source)
    psi = np.zeros(9, dtype=np.complex128)
    psi[source] = 1.0
    rho0 = np.outer(psi, psi.conj())
    history = evolve(cfg, h, rho0)

    return {
        "status": "SYNTHETIC_CLASSICAL_SIMULATION",
        "model": "single_excitation_3x3_tight_binding",
        "config": asdict(cfg),
        "source_index": source,
        "target_index": site_index(*cfg.target),
        "hamiltonian_hermitian": bool(np.allclose(h, h.conj().T)),
        "history": history,
    }


if __name__ == "__main__":
    print(json.dumps(run_transport_experiment(), indent=2))
