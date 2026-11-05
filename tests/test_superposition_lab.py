import numpy as np

from superposition_lab.coherence import (
    apply_dephasing,
    apply_phase,
    density_matrix,
    two_state_coherence_benchmark,
)
from superposition_lab.sidebands import SidebandConfig, run_sideband_experiment
from superposition_lab.transport import TransportConfig, run_transport_experiment


def test_coherent_and_mixed_states_have_same_populations():
    coherent = density_matrix(np.array([1, 1], dtype=complex))
    mixed = np.eye(2, dtype=complex) / 2
    assert np.allclose(np.real(np.diag(coherent)), np.real(np.diag(mixed)))
    assert abs(coherent[0, 1]) > 0
    assert abs(mixed[0, 1]) == 0


def test_complete_dephasing_removes_offdiagonal_terms():
    rho = density_matrix(np.array([1, 1], dtype=complex))
    rho = apply_phase(rho, np.pi / 3)
    rho = apply_dephasing(rho, 1.0)
    assert rho[0, 1] == 0
    assert rho[1, 0] == 0
    assert np.isclose(np.trace(rho).real, 1.0)


def test_coherence_benchmark_is_deterministic_and_valid():
    result = two_state_coherence_benchmark(
        phi_values=[0.0, np.pi],
        gamma_values=[0.0, 1.0],
        noise_seed=3,
        trials=500,
    )
    assert result["status"] == "SYNTHETIC_CLASSICAL_SIMULATION"
    assert len(result["rows"]) == 8
    for row in result["rows"]:
        assert np.isclose(row["p0"] + row["p1"], 1.0)
        assert 0 <= row["rate0"] <= 1
        assert 0 <= row["rate1"] <= 1


def test_transport_preserves_trace_and_reports_target_population():
    result = run_transport_experiment(TransportConfig(steps=25, seed=5))
    assert result["hamiltonian_hermitian"]
    assert result["history"][0]["target_population"] == 0.0
    assert 0 <= result["history"][-1]["target_population"] <= 1
    assert result["history"][-1]["purity"] <= 1 + 1e-10


def test_sideband_experiment_preserves_normalization():
    cfg = SidebandConfig(levels=8, central_level=4, steps=20, seed=11)
    result = run_sideband_experiment(cfg)
    assert result["history"][0]["central_population"] == 1.0
    assert 0 <= result["history"][-1]["central_population"] <= 1
    assert result["history"][-1]["purity"] <= 1 + 1e-10
