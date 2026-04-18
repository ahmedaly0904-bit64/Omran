import numpy as np
from nation import Nation 


class WorldGrid:
    """
    Manages the spatial environment of the simulation.
    Each cell on the grid holds the 'presence strength'
    of a civilization (0.0 → 1.0).

    Responsibilities:
    - Track which nation controls which cell
    - Spread civilizations across the grid over time
    - Resolve conflicts when two civilizations meet
    """

    def __init__(self, width: int = 50, height: int = 50):
        self.width  = width
        self.height = height

        self.presence = np.zeros((height, width))

        self.ownership = np.empty((height, width), dtype=object)

    def place_nation(self, nation, x: int, y: int):
        self.presence[y][x]  = 1.0
        self.ownership[y][x] = nation

    def get_neighbors(self, nation: Nation ) -> list:
        """
        Return all alive nations within 1 cell (Moore neighborhood).
        This replaces Mesa's grid.get_neighbors().
        """
        neighbors = set()
        ys, xs = np.where(self.ownership == nation)

        for y, x in zip(ys, xs):
            for dy, dx in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                ny, nx = y + dy, x + dx
                if not (0 <= ny < self.height and 0 <= nx < self.width):
                    continue
                neighbor_owner = self.ownership[ny][nx]

                if neighbor_owner is not None and neighbor_owner is not nation and neighbor_owner.is_alive:
                    neighbors.add(neighbor_owner)

        return list(neighbors)


    def spread(self, nations: list):
        """
        Expand each civilization to neighboring cells.
        Spread rate depends on population relative to carrying capacity.
        Called once per simulation step (year).
        """
        new_presence  = self.presence.copy()
        new_ownership = self.ownership.copy()

        for nation in nations:
            if not nation.is_alive:
                continue

            # How fast this nation spreads (0.0 → 1.0)
            spread_rate = nation.population / nation.carrying_capacity
            spread_rate = min(1.0, spread_rate)   # cap at 1.0

            ys, xs = np.where(self.ownership == nation)

            for y, x in zip(ys, xs):
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ny, nx = y + dy, x + dx

                    if not (0 <= ny < self.height and 0 <= nx < self.width):
                        continue

                    neighbor_owner = self.ownership[ny][nx]

                    if neighbor_owner is None:
                        new_strength = self.presence[y][x] * spread_rate * 0.5
                        if new_strength > new_presence[ny][nx]:
                            new_presence[ny][nx]  = new_strength
                            new_ownership[ny][nx] = nation

                    elif neighbor_owner is not nation:
                        self._resolve_conflict(
                            nation, neighbor_owner,
                            ny, nx,
                            new_presence, new_ownership
                        )

        self.presence  = new_presence
        self.ownership = new_ownership


    def _resolve_conflict(
        self,
        attacker,
        defender,
        y: int, x: int,
        new_presence:  np.ndarray,
        new_ownership: np.ndarray,

    ):
        """
        Two civilizations meet on a cell — the stronger one wins.
        Strength = population × presence value at the contested cell.
        
        """
        attacker_strength = attacker.population * self.presence[y][x]
        defender_strength = defender.population * self.presence[y][x]

        if attacker_strength > defender_strength:
            new_presence[y][x]  = self.presence[y][x] * 0.7  # war destroys
            new_ownership[y][x] = attacker

            attacker.win_clash()
            defender.lose_clash()
        else:
            new_presence[y][x]  = self.presence[y][x] * 0.8
            attacker.lose_clash()
            defender.win_clash()


    def display(self, nations: list):
        symbol_map = {n: n.name[-1] for n in nations}

        for y in range(self.height):
            for x in range(self.width):
                owner = self.ownership[y][x]
                if owner is not None and owner.is_alive:
                    print(f"{symbol_map[owner]} ", end="")
                else:
                    print(". ", end="")
            print()
        print("=" * (self.width * 2))

    def get_snapshot(self,nations) -> np.ndarray:
        """
        Return a numeric grid for Plotly Heatmap (Phase 4).
        Each cell = index of owning nation (0 = empty, 1/2/3 = nation).
        """
        nation_ids={}
        snapshot = np.zeros((self.height, self.width))
        for i,nation in enumerate(nations):
            nation_ids[nation]=i+1
        for y in range(self.height):
            for x in range(self.width):
                owner = self.ownership[y][x]
                if owner is not None:
                    snapshot[y][x] = nation_ids[owner]
                else:
                    snapshot[y][x] = 0
        return snapshot