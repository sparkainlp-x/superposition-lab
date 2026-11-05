"""Two-state superposition benchmark.

The coherent state and the dephased control have identical populations in
the computational basis. Only the coherent state has off-diagonal entries,
so a phase-sensitive analyzer can distinguish them.
"""

from __future__ import annotations

import json
import numpy as np


def density_matrix(state):
    """Return the normalized projector for a normalized state vector."""
    state = np.asarray(state, dtype=np.complex128).reshape(-1)
    norm = np.linalg.norm(state)
    if not np.isfinite(norm) or norm <= 0:
        raise ValueError("state must have finite positive norm")
    psi = state / norm
    rho = np.outer(psi, psi.conj())
    return 0.5 * (rho + rho.conj().T)


def apply_phase(rho, phi):
    """Apply a relative phase between basis states 0 and 1."""
    u = np.array([[1.0, 0.0], [0.0, np.exp(1j * phi)]], dtype=np.complex128)
    return u @ rho @ u.conj().T


def apply_dephasing(rho, gamma):
    """Apply complete dephasing in the computational basis by amount gamma."""
    if gamma < 0 or gamma > 1:
        raise ValueError("gamma must lie in [0, 1]")
    out = rho.copy()
    out[0, 1] *= 1.0 - gamma
    out[1, 0] *= 1.0 - gamma
    return 0.5 * (out + out.conj().T)


def apply_analyzer(rho, theta):
    """Apply a balanced basis rotation followed by a computational readout."""
    c, s = np.cos(theta), np.sin(theta)
    u = np.array([[c, -s], [s, c]], dtype=np.complex128)
    return u @ rho @ u.conj().T


def populations(rho):
    """Return the real diagonal populations."""
    return np.real(np.diag(rho))


def coherence(rho):
    """Return the magnitude of the single off-diagonal coherence."""
    return float(abs(rho[0, 1]))


def two_state_coherence_benchmark(phi_values, gamma_values, noise_seed=7, trials=2000):
    """Run paired coherent-versus-mixed-state trials.

    Returns measured populations, coherence and analyzer outcome rates.
    The analyzer is a basis rotation; measurement outcomes are sampled from
    the resulting diagonal populations.
    """
    phi_values = np.asarray(phi_values, dtype=float)
    gamma_values = np.asarray(gamma_values, dtype=float)
    if trials < 1:
        raise ValueError("trials must be positive")
    if np.any((gamma_values < 0) | (gamma_values > 1)):
        raise ValueError("all gamma values must lie in [0, 1]")

    coherent = density_matrix(np.array([1.0, 1.0], dtype=np.complex128))
    mixed = np.eye(2, dtype=np.complex128) / 2.0
    rng = np.random.default_rng(noise_seed)
    rows = []

    for gamma in gamma_values:
        for phi in phi_values:
            for label, rho0 in (("coherent", coherent), ("mixed", mixed)):
                rho = apply_phase(rho0, float(phi))
                rho = apply_dephasing(rho, float(gamma))
                rho_out = apply_analyzer(rho, np.pi / 4.0)
                p = populations(rho_out)
                counts = rng.multinomial(trials, p / p.sum())
                rows.append({
                    "arm": label,
                    "phi": float(phi),
                    "gamma": float(gamma),
                    "input_coherence": coherence(rho),
                    "p0": float(p[0]),
                    "p1": float(p[1]),
                    "count0": int(counts[0]),
                    "count1": int(counts[1]),
                    "rate0": float(counts[0] / trials),
                    "rate1": float(counts[1] / trials),
                })

    return {
        "status": "SYNTHETIC_CLASSICAL_SIMULATION",
        "trials": int(trials),
        "noise_seed": int(noise_seed),
        "rows": rows,
    }


if __name__ == "__main__":
    result = two_state_coherence_benchmark(
        phi_values=[0.0, np.pi / 2, np.pi],
        gamma_values=[0.0, 0.5, 1.0],
        trials=1000,
    )
    print(json.dumps(result, indent=2))
