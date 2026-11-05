# Superposition Lab

**SYNTHETIC classical software simulation.** This repository explores three
quantum-inspired concepts: two-state coherence, coherent excitation transport
on a 3x3 lattice, and truncated electron energy-sideband control.

It does **not** simulate quantum hardware, create energy, model a physical
particle accelerator, or establish a new-physics claim. It is intended as a
small, reproducible companion to `membrane-arena-3x3`.

## Play the game

**Superposition Arena** is a standalone interactive scientific game:
[Open `game/index.html`](game/index.html).

Tune phase, coupling and dephasing to guide a coherent excitation to the
gold target. See [`docs/GAME.md`](docs/GAME.md) for the model and limits.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy pytest
pip install -e .
```

## Run

```bash
python -m superposition_lab.cli coherence --trials 2000
python -m superposition_lab.cli transport --steps 200
python -m superposition_lab.cli sidebands --steps 50
```

## Experiments

| Command | Model | Scientific question |
|---|---|---|
| `coherence` | Two-state density matrices | Does a phase-sensitive analyzer distinguish a coherent state from a population-matched mixed state? |
| `transport` | One excitation on a 3x3 tight-binding lattice | How do disorder and dephasing affect delivery to a target site? |
| `sidebands` | Truncated energy-sideband ladder | How does phase noise affect coherent population redistribution? |

## Evidence policy

All outputs are labelled `SYNTHETIC_CLASSICAL_SIMULATION`. Results are
exploratory unless a preregistered benchmark, held-out seeds, uncertainty
estimates and an independent implementation check are added.
