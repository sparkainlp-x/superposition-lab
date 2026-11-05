"""Command-line interface for the synthetic superposition lab."""

from __future__ import annotations

import argparse
import json
import numpy as np

from .coherence import two_state_coherence_benchmark
from .sidebands import SidebandConfig, run_sideband_experiment
from .transport import TransportConfig, run_transport_experiment


def main():
    parser = argparse.ArgumentParser(
        description="SYNTHETIC superposition, transport and sideband experiments."
    )
    sub = parser.add_subparsers(dest="experiment", required=True)

    coherence = sub.add_parser("coherence", help="two-state coherence benchmark")
    coherence.add_argument("--trials", type=int, default=2000)
    coherence.add_argument("--seed", type=int, default=7)

    transport = sub.add_parser("transport", help="3x3 coherent-transport model")
    transport.add_argument("--coupling", type=float, default=0.10)
    transport.add_argument("--disorder", type=float, default=0.20)
    transport.add_argument("--dephasing", type=float, default=0.05)
    transport.add_argument("--steps", type=int, default=200)
    transport.add_argument("--seed", type=int, default=42)

    sideband = sub.add_parser("sidebands", help="energy-sideband control model")
    sideband.add_argument("--levels", type=int, default=16)
    sideband.add_argument("--coupling", type=float, default=1.0)
    sideband.add_argument("--phase-noise", type=float, default=0.0)
    sideband.add_argument("--steps", type=int, default=50)
    sideband.add_argument("--seed", type=int, default=17)

    args = parser.parse_args()
    if args.experiment == "coherence":
        result = two_state_coherence_benchmark(
            phi_values=[0.0, np.pi / 2, np.pi],
            gamma_values=[0.0, 0.25, 0.5, 1.0],
            noise_seed=args.seed,
            trials=args.trials,
        )
    elif args.experiment == "transport":
        result = run_transport_experiment(TransportConfig(
            coupling=args.coupling,
            disorder=args.disorder,
            dephasing=args.dephasing,
            steps=args.steps,
            seed=args.seed,
        ))
    else:
        result = run_sideband_experiment(SidebandConfig(
            levels=args.levels,
            coupling=args.coupling,
            phase_noise=args.phase_noise,
            steps=args.steps,
            seed=args.seed,
        ))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
