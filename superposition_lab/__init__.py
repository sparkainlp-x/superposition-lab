"""SYNTHETIC superposition and coherent-transport experiments.

This package implements classical NumPy simulations of quantum-inspired
state evolution. It is not quantum hardware, a physical accelerator, a
medical device, or a claim of energy creation.
"""

from .coherence import two_state_coherence_benchmark
from .transport import run_transport_experiment
from .sidebands import run_sideband_experiment

__all__ = [
    "two_state_coherence_benchmark",
    "run_transport_experiment",
    "run_sideband_experiment",
]
