import random
from nation import Nation
from grid import WorldGrid



class WorldModel:
    """
    The simulation engine — manages all nations and the grid.
    Pure Python + NumPy — no external framework required.
    """

    GRID_WIDTH  = 50
    GRID_HEIGHT = 50
    def __init__(self,starting_nations: list[Nation]):
        self.grid = WorldGrid(self.GRID_WIDTH, self.GRID_HEIGHT)

        self.nations = starting_nations

        self.year = 0

        print("\n--- Starting Simulation ---")
        self._place_on_grid()
        print("---------------------------\n")

    def _place_on_grid(self):
        used_positions = set()
        for nation in self.nations:
            while True:
                x = random.randint(0, self.GRID_WIDTH  - 1)
                y = random.randint(0, self.GRID_HEIGHT - 1)
                if (x, y) not in used_positions:
                    self.grid.place_nation(nation, x, y)
                    used_positions.add((x, y))
                    break



    def step(self):
        self.year += 1

        random.shuffle(self.nations)

        for nation in self.nations:
            if nation.is_alive:
                neighbors = self.grid.get_neighbors(nation)
                nation.step(neighbors)
        self.grid.spread(self.nations)



    def run(self, years: int):
        for _ in range(years):
            self.step()

    def display(self):
        self.grid.display(self.nations)
    def get_snapshot(self):
        return self.grid.get_snapshot(self.nations)