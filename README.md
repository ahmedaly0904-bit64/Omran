# Project Omran — عُمران
### Civilization Simulation

> *"To simulate how shared ideas shape the rise and fall of civilizations —*
> *translating Ibn Khaldun's theory of Asabiyyah into computational physics."*

---

## Why Omran?

Named after Ibn Khaldun's concept of *'ilm al-'umran* — the systematic study
of civilization, urbanization, and social organization.

This project asks a simple but profound question:

> **How does a civilization rise — and why does another one collapse?**

The answer, according to Ibn Khaldun, lies not only in resources and armies —
but in **ideas** and **social cohesion (Asabiyyah)**. This simulation translates
that theory into equations and code.

---

## What the Code Does Right Now

Three forces drive every civilization in the simulation:

- **Population** — grows logistically via RK4, collapses under famine
- **Territory** — spreads across a 2D NumPy grid, contested by warfare
- **Food** — produced each year with weather randomness, consumed by population

When two civilizations meet on the grid, the stronger one takes the cell.
Both sides take losses. Civilizations expand until they hit each other — or collapse.

---

## Project Structure

```
omran/
├── src/
│   ├── functions.py   # RK4 solver + stochastic growth — pure math, no dependencies
│   ├── nation.py      # Nation class — population, food, warfare behavior
│   ├── grid.py        # WorldGrid — spatial map, neighbor detection, conflict resolution
│   ├── world.py       # WorldModel — orchestrator, runs the simulation loop
│   └── main.py        # Entry point — creates nations, runs, renders Plotly output
├── MVP/               # v1 — Jupyter notebook, Mesa + Matplotlib (preserved for reference)
└── README.md
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| NumPy | Spatial grid and vectorized operations |
| Plotly | Interactive heatmap and population charts |

> No game engines. No ABM frameworks. Pure Python + Math.

---

## Architectural Decisions

This project went through a deliberate architectural refactor.
These are the decisions that shaped the current structure:

**Dependency Injection**
`WorldModel` does not create nations internally.
Nations are defined in `main.py` and passed in as a parameter.
The simulation engine is decoupled from the scenario — you can swap
civilizations without touching the engine.

**Single Source of Truth — Spatial Data**
Nations have no `x` or `y` attributes.
`WorldGrid` owns the `ownership` array and is the only place that knows
where any civilization is. This prevents state drift between the agent
and the map.

**Spatial Logic Belongs in the Grid**
`get_neighbors()` was moved from `WorldModel` to `WorldGrid`.
It queries the `ownership` array directly via `np.where` instead of
comparing coordinate attributes on Nation objects.

**Combat SRP**
`WorldGrid._resolve_conflict()` does not call `receive_damage()` directly.
It calls `win_clash()` and `lose_clash()` on Nation — keeping the grid
responsible for spatial outcomes and the Nation responsible for
its own demographic response.

**Output is Not the Engine's Problem**
`print_summary()` was moved out of `WorldModel` into `main.py`.
The simulation engine returns data. Formatting is the caller's responsibility.

---

## Technical Principles

### Population Growth
```
dP/dt = r x P x (1 - P/K)
```
Solved via RK4 at each time step. Integer population is recovered via
a Monte Carlo step (stochastic rounding) to avoid float drift.

### Territorial Expansion
```
spread_rate = population / carrying_capacity
```
Each year, a civilization expands to neighboring cells proportional to
how close it is to its carrying capacity.

### Warfare on the Grid
```
attacker_strength = population x presence_value
defender_strength = population x presence_value

winner takes the cell — both sides take losses
```

---

## Development Phases

| Phase | Description | Status |
|---|---|---|
| 0 | Architectural Refactor — DI, SRP, Single Source of Truth | ✅ Done |
| 1 | Core OOP — Nation + World classes | ✅ Done |
| 2 | Mathematical Engine — RK4 + Stochastic Growth | ✅ Done |
| 3 | Spatial Environment — NumPy Grid + Spread + Warfare | ✅ Done |
| 4 | Plotly Dashboard — Interactive map and population curves | ✅ Done |
| 5 | Idea Spread — SIR model for ideological diffusion | ⏳ |
| 6 | Advanced Logic — Economy, Trade, Collapse scenarios | ⏳ |

---

## What's Coming

**Phase 5 — Idea Spread**

This is the intellectual core of the project — the part that makes it Omran
and not just another population simulator.

The plan: add `idea_strength` and `asabiyyah` as dynamic variables to each
civilization. Ideas spread between neighboring civilizations using a modified
SIR model (Susceptible → Infected → Resistant). A civilization exposed to a
stronger idea may adopt it — strengthening its cohesion — or resist it,
triggering conflict.

Asabiyyah then decays when the driving idea weakens:

```
dA/dt = -0.01 x (1 - idea_strength)
```

The current architecture makes this possible cleanly: nations are self-contained,
the grid is spatially independent, and neighbors are already detected correctly.
Phase 5 adds a new layer on top of what exists — it does not require rebuilding
anything.

---

## Intellectual Lineage

- **Ibn Khaldun** — *Muqaddimah* (1377) — Theory of Asabiyyah and civilizational cycles
- **Peter Turchin** — *Cliodynamics* — Mathematical modeling of historical dynamics
- **Thomas Malthus** — Population and resource limits

---

*Developed as a personal project in computational physics and complex systems.*

*Copyright 2026 Ahmed. All rights reserved.*