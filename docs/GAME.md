# Superposition Arena

**SYNTHETIC educational scientific game.** Superposition Arena lets a player
tune phase, coupling and dephasing to guide one quantum-inspired excitation
across a 3×3 lattice.

It is a classical JavaScript simulation. It does **not** simulate quantum
hardware, create energy, model a physical particle accelerator, or make a
new-physics claim.

## Play

Open [`game/index.html`](../game/index.html), or serve the repository locally:

```bash
python -m http.server 8000
```

Then visit:

```text
http://localhost:8000/game/
```

## Scientific model

The game represents one excitation as a complex amplitude vector over nine
sites. A nearest-neighbour tight-binding Hamiltonian determines how amplitude
moves between sites. Relative phase controls can produce constructive or
destructive interference; dephasing reduces phase relationships.

The displayed quantities are:

- **Target delivery:** population at the selected target site.
- **Mean coherence:** a synthetic off-diagonal magnitude measure.
- **Control budget:** a game constraint on coupling and dephasing use.

## Goal

Reach the required target delivery before exhausting the control budget.
Later levels add disorder, dephasing and tighter budgets.

## Limitations

This is an exploratory, game-oriented model. It is not a validated physical
transport model, a quantum computer, a particle accelerator, a medical device,
or a consciousness model. Results apply only to this simulation.
