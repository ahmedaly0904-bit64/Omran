import numpy as np
from collections import defaultdict
from nation import Nation


class WorldGrid:
    """
    Manages the spatial environment of the simulation.
    Responsibilities:
    - Track which nation controls which cell
    - Spread civilizations across the grid over time
    - Resolve conflicts when two civilizations meet
    """

    def __init__(self, width: int = 50, height: int = 50):
        self.width  = width
        self.height = height
        self.ownership = np.empty((height, width), dtype=object)

    def place_nation(self, nation, x: int, y: int):
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
        new_ownership = self.ownership.copy()
        for nation in nations:
            if not nation.is_alive:
                continue
            spread_rate = nation.population / nation.carrying_capacity
            spread_rate = min(1.0, spread_rate)

            owned = self.ownership == nation
            empty_right = self.ownership[:, 1:] == np.array(None)
            empty_left = self.ownership[:, :-1] == np.array(None)
            empty_top = self.ownership[:-1, :] == np.array(None)
            empty_down = self.ownership[1:, :] == np.array(None)

            can_spread = owned[:,:-1] & empty_right
            new_ownership[:, 1:][can_spread] = nation
            can_spread = owned[:, 1:] & empty_left
            new_ownership[:, :-1][can_spread] = nation
            can_spread = owned[1:, :] & empty_top
            new_ownership[:-1, :][can_spread] = nation
            can_spread = owned[:-1, :] & empty_down
            new_ownership[1:, :][can_spread] = nation


        self.ownership = new_ownership
        snapshot,id_to_nation = self.get_snapshot(nations)
        for nation_id, nation in id_to_nation.items():
            nation.set_territory(int(np.count_nonzero(snapshot == nation_id)))
        horizontal = snapshot[:, :-1] != snapshot[:, 1:]
        vertical = snapshot[:-1, :] != snapshot[1:, :]
        ys_h , xs_h = np.where(horizontal)
        ys_v , xs_v = np.where(vertical)
        border_lengths = defaultdict(int)

        for y, x in zip(ys_h, xs_h):
            if snapshot[y, x] == 0 or snapshot[y, x + 1] == 0:
                continue
            n1 = id_to_nation[snapshot[y, x]]
            n2 = id_to_nation[snapshot[y, x + 1]]
            pair = frozenset({n1, n2})
            border_lengths[pair] += 1

        for y, x in zip(ys_v, xs_v):
            if snapshot[y, x] == 0 or snapshot[y + 1, x] == 0:
                continue
            n1 = id_to_nation[snapshot[y, x]]
            n2 = id_to_nation[snapshot[y + 1, x]]
            pair = frozenset({n1, n2})
            border_lengths[pair] += 1
        for pair, length in border_lengths.items():
            n1,n2 = tuple(pair)
            if not n1.is_alive or not n2.is_alive:
                continue
            n1.border_attrition(length)
            n2.border_attrition(length)



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
        id_to_nation={}
        for i,nation in enumerate(nations):
            nation_ids[nation]=i+1
            id_to_nation[i+1] = nation

        get_id = np.vectorize(lambda nation: nation_ids.get(nation, 0))
        snapshot = get_id(self.ownership)

        return snapshot,id_to_nation

    def release(self,nation):
        self.ownership[self.ownership == nation] = None
