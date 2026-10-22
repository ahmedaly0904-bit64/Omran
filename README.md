# Project Omran — عُمران

An agent-based simulation of the rise and decline of states, built on Ibn
Khaldun's *'ilm al-'umran* — علم العمران, the study of how human settlement
organises itself and why it comes apart. Pure Python + NumPy; no ABM framework.

Nations grow logistically, live off the land they hold, expand across a 2D
grid, wear each other down where they touch, and pass ideas to their
neighbours.

This document describes **what the code does**, not what it is meant to do.
Every mechanism is marked implemented, partial, or absent. Where the code
departs from the theory it is named as a departure, not glossed over.

**Verified against `src/` on 26 August 2026.**

---

## Running it

```bash
pip install -r requirements.txt
python src/main.py
```

Opens a Plotly window: territory heatmap on the left, population curves on the
right. `main.py` also prints a per-nation summary table.

Requires `numpy>=1.21` and `plotly>=5.9`. `src/` is not a package — `main.py`
imports its siblings directly, so run it from inside `src/` or with `src/` on
the path.

---

## Theory ↔ code

The vocabulary below is Ibn Khaldun's. It is used throughout this document
because it is more precise about *this* subject than the generic English —
`asabiyyah` is not "morale", and `'umran` is not "civilisation" in the vague
sense.

| المصطلح | Term | Where it lives in the code | Status |
|---|---|---|---|
| العُمران البشري | Human settlement — people on land | `Nation.population` + `WorldGrid.ownership` | implemented |
| المَعاش | Livelihood — what the land yields | `food_production`, `carrying_capacity` | implemented |
| نطاق الدولة | The reach of the state | `Nation.territory` | implemented, ungated |
| ضَعْف الأطراف | Weakening at the extremities | `border_attrition()` | implemented |
| المُغالَبة | Contest between neighbours | `_attempt_warfare()`, `attack()` | implemented |
| الدَّعوة | The call — an idea carried between groups | `Traits` (SIR), `WorldModel.spread_idea()` | implemented |
| العَصبية | Group feeling — the cohesion that founds a state | `asabiyyah.py` | **empty** |
| الترف | Affluence — what dissolves cohesion | `population / carrying_capacity` | computed, unused |
| الهَرَم | Senescence — the decline phase | — | **absent (gap 1)** |

The last three are the missing half of the model. Without them the simulation
produces growth and stalemate, never a cycle.

---

## Module map

| File | Owns | Never does |
|---|---|---|
| `functions.py` | RK4, logistic derivative, Monte Carlo rounding | Know what a nation is |
| `traits.py` | SIR fractions `s`/`i`/`r` and their invariant | Know population counts |
| `nation.py` | Head-count, food stock, warfare, famine | Know where it is on the map |
| `grid.py` | `ownership` array, neighbours, expansion, border lengths | Modify a nation's population |
| `world.py` | The yearly loop, idea spread, ordering | Print or render anything |
| `main.py` | The scenario, the seed, all output | Contain simulation logic |
| `asabiyyah.py` | *(empty — see Open Design)* | |

Spatial truth lives only in `WorldGrid.ownership`. Nations have no `x`/`y`.

---

## The yearly step

`WorldModel.step()` runs this order, and the order is load-bearing:

```
1. shuffle nations                      (war target selection only)
2. for each living nation:
       update food  →  update population  →  maybe declare war
3. grid.spread()      expand, recount territory, apply border attrition
4. spread_idea()      gather force of infection, apply once
5. recover_idea()
6. append to pop_history
```

Steps 4 and 5 are order-independent by construction. Step 2 is not — the
shuffle exists so the bias does not always favour the same nation.

---

## Population — العُمران البشري — implemented

```
dP/dt = r × P × (1 − P/K)
```

Solved by 4th-order Runge-Kutta (`functions.solve_rk4`) with `TIME_STEP = 1`.
The float result becomes an integer through `functions.monte_carlo()`, which
rolls a die against the fractional part rather than truncating it.

Every path that changes population — growth, famine, war, attrition — goes
through `Nation.change_populations()`. Its body is one line; it exists as a
single control point, not for its length.

---

## Land and livelihood — المَعاش — implemented

Ibn Khaldun treats livelihood as the base of settlement: people cluster where
the land feeds them, and the size of a settlement is bounded by what its
territory yields. The code takes this literally.

`territory` (cell count) is the only stored quantity. Both derived values are
`@property`, so they cannot fall out of step with the map:

```
food_production = territory × FOOD_PER_CELL
K               = food_production / CONSUMPTION_PER_PERSON
```

`WorldGrid.spread()` counts each nation's cells with `np.count_nonzero` and
calls `Nation.set_territory()` — it sends a spatial fact and lets the nation
interpret it, the same contract used for border attrition.

`FOOD_PER_CELL` is derived from a stated assumption, not tuned:

```
one cell        = an agricultural region feeding ~2000 people
PEOPLE_PER_CELL = 2000
FOOD_PER_CELL   = PEOPLE_PER_CELL × CONSUMPTION_PER_PERSON = 4000
```

Yearly food balance:

```
production  = territory × FOOD_PER_CELL × uniform(0.8, 1.2)
consumption = population × CONSUMPTION_PER_PERSON
```

If the stock goes negative, deaths scale with the per-person deficit by
`FAMINE_INTENSITY_COEFFICIENT = 0.3`, the stock resets to 0, and
`famine_count` increments.

---

## Reach of the state — نطاق الدولة — implemented, ungated

Vectorised NumPy slicing on the `ownership` array: every living nation claims
every adjacent empty cell (4-neighbourhood) each year, at maximum speed.

```python
spread_rate = nation.population / nation.carrying_capacity   # computed
spread_rate = min(1.0, spread_rate)                          # never read
```

Both lines run every year and the result is discarded. **Demography has no
effect on reach.** In Ibn Khaldun the reach of a state is proportional to the
strength of its asabiyyah; here it is proportional to nothing at all.

---

## Contest and attrition — المُغالَبة وضَعْف الأطراف — implemented

Two independent mechanisms.

**Declared war** (`Nation._attempt_warfare`) — with probability
`WARFARE_PROBABILITY = 0.1` a nation picks a random living neighbour and
attacks only if it has more people. `ENEMY_DAMAGE = 0.1`,
`ATTACKER_DAMAGE = 0.04`.

**Border attrition** (`WorldGrid.spread` → `Nation.border_attrition`) — every
touching pair loses population each year:

```
damage = min(0.5, 0.2 × border_length / population)
```

This lands close to a Khaldunian observation without having been designed for
it: a state's grip weakens at its extremities, so the further its frontier
runs from its demographic core, the more it costs to hold. Here that cost is
literal — attrition scales with border length and divides by population, so a
long frontier held by few people is expensive, and the same frontier held by
many is cheap.

Border length is aggregated **once per nation-pair** with `defaultdict` +
`frozenset`, not per cell. Per-cell application was the Phase-3 mass-extinction
bug: a nation with 40 border cells took the damage 40 times a year.

Both mechanisms route through `receive_damage()`, which converts fractional
deaths with `monte_carlo()`.

---

## The call — الدَّعوة — implemented

An SIR model over **fractions**, one instance per nation. Ibn Khaldun pairs
asabiyyah with *da'wa* — the call — as the two things a state needs: cohesion
to hold together, and a shared idea to hold to. Only the second is modelled so
far.

```
λ = Σ over grid neighbours of  β × i_neighbour      β = 0.05
    s → i  by  min(1, λ)
    i → r  by  γ                                    γ = 0.1
```

`Traits` stores `_S`/`_I`/`_R` privately with read-only properties. Both
operations are conservative transfers — compute the moved amount, subtract from
source, add to target — and `_check()` runs after each one.

The force of infection is summed over all neighbours **before** it is applied,
so the result does not depend on iteration order. Same two-phase pattern
`WorldGrid.spread()` uses with `ownership.copy()`.

Births and deaths change the head-count only; they leave `s`/`i`/`r` untouched.
This assumes mortality is homogeneous across the three compartments.

The initial carrier is a scenario decision, not an engine one — `main.py` calls
`random.choice(nations).idea.infect(0.01)` before the run. Without it the model
is mathematically correct and completely inert.

---

## Invariants

| Invariant | Enforced by | On violation |
|---|---|---|
| `s + i + r == 1.0` | `Traits._check()` after every transfer | renormalise within `1e-6`, else `ValueError` carrying the raw values |
| `population >= 0` | `Nation.change_populations()` | clamped at 0 |
| every cell has at most one owner | `ownership` is a single array | — |

Verification run: 4 nations × 300 years → `s+i+r == 1.000000000000` in every
nation, no exceptions raised.

---

## Constants

| Constant | Value | File |
|---|---|---|
| `GRID_WIDTH` × `GRID_HEIGHT` | 50 × 50 | `world.py` |
| `IDEA_TRANSMISSION_RATE` (β) | 0.05 | `world.py` |
| `RECOVERY_RATE` (γ) | 0.1 | `world.py` |
| `CONSUMPTION_PER_PERSON` | 2 | `nation.py` |
| `PEOPLE_PER_CELL` | 2000 | `nation.py` |
| `FOOD_PER_CELL` | derived → 4000 | `nation.py` |
| `WARFARE_PROBABILITY` | 0.1 | `nation.py` |
| `ENEMY_DAMAGE` / `ATTACKER_DAMAGE` | 0.1 / 0.04 | `nation.py` |
| `FAMINE_INTENSITY_COEFFICIENT` | 0.3 | `nation.py` |
| `TIME_STEP` | 1 year | `nation.py` |

`random.seed(42)` in `main.py` makes every run reproducible. Remove it to
sample different histories.

---

## Open gaps

Measured, not suspected. Figures are from a 500-year run, 3 nations, seed 42.

**1. Land is never given back — no هَرَم.**
`ownership` is written on expansion and never cleared. There is no retreat, no
conquest, and an extinct nation keeps its cells forever. In the reference run
an extinct nation held 1324 of 2500 cells from year 100 onward, walling its
neighbours in; the survivors' territory did not change for 400 years.

This is the single most consequential gap. A state that cannot lose ground
cannot decline, and a model of Ibn Khaldun without decline is half a model.

**2. Livelihood is inert.**
Production depends on land alone, so a nation of one person farms its entire
empire. Stock grows without bound (2.5×10⁹ by year 500) and `famine_count`
stays at 0 for every nation in every run. `K` and the food balance are two
ceilings derived from the same fact — as written, one is redundant. Labour
does not enter the yield at all.

**3. Reach ignores demography.**
`spread_rate` is computed and discarded; a nation of 1 expands as fast as a
nation of a million.

**4. `src/` is not a package.**
Flat imports (`from nation import Nation`) mean the code only runs with `src/`
on the path.

---

## Design decisions

**Dependency injection.** `WorldModel` does not create nations. The scenario
lives in `main.py`; the engine works with any starting condition.

**One source of truth per fact.** Position lives only in `ownership`.
Head-count lives only in `Nation`. `food_production`, `carrying_capacity` and
the SIR compartments are derived, never stored — a stored duplicate of a
derived value is exactly what caused the population/SIR drift bug.

**The grid sends facts, not commands.** `WorldGrid` never modifies population.
It calls `nation.border_attrition(border_length)` and lets the nation decide
what that means demographically.

**Rounding stays out of stored state.** `monte_carlo()` converts fractional
people to integers without bias. Truncating instead created an absorbing state:
a nation at one person took `int(1 × 0.5) = 0` deaths per year and became
immortal while keeping its whole territory.

**Output is not the engine's problem.** `print_summary()` and all Plotly code
live in `main.py`. The engine returns data.

---

## Open design: العَصبية

`asabiyyah.py` exists and is empty. Decided so far:

- **Generational, not contagious.** Asabiyyah is internal to a group, strongest
  at founding and thinning as the generations pass. It is *not* transmitted
  between nations, so it does not reuse the SIR machinery of الدَّعوة. This
  follows the Muqaddimah's own account: a dynasty rarely outlives three
  generations — the founders who hold it by hardship, the sons who saw them do
  it, and the grandsons who only inherited it.
- **Effect in `border_attrition()` only**, not in `receive_damage()` —
  otherwise war damage would count it twice.
- **الترف — affluence** = `population / carrying_capacity`. A group living well
  below what its land can feed is still austere; one pressed against its
  ceiling has settled into comfort. This is the same ratio `spread_rate`
  already computes and discards.

The earlier proposal `dA/dt = -0.01 × (1 - idea_strength)` is rejected: it made
asabiyyah a function of idea spread, which contradicts the generational reading
above and collapses العصبية and الدَّعوة into one quantity.

---

## Intellectual lineage

- **ابن خلدون** — *المقدمة* (1377) — العصبية, أطوار الدولة, the dynastic cycle
- **Peter Turchin** — *Cliodynamics* — mathematical modelling of historical dynamics
- **Thomas Malthus** — population against resource limits

---

## Development phases

| Phase | Scope | Status |
|---|---|---|
| 1 | Core OOP — Nation, World, Grid, Traits | done |
| 2 | Visualisation — Plotly heatmap + population curves | done |
| 3 | Spatial environment — grid, expansion, borders | reach ungated (gap 3) |
| 4 | المَعاش — land-driven food and carrying capacity | inert (gap 2) |
| 5 | Interaction — contest done, trade not started | partial |
| 6 | العَصبية | not started |

---

*Personal project in computational physics and complex systems.*
*Copyright 2026 Ahmed Aly. All rights reserved.*
