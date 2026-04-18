from mesa import Agent
from functions import *

# Constants for simulation
WARFARE_PROBABILITY = 0.1
FAMINE_INTENSITY_COEFFICIENT = 0.3
ENEMY_DAMAGE = 0.1
ATTACKER_DAMAGE = 0.04
TIME_STEP = 1
CONSUMPTION_PER_PERSON = 10

class NationAgent(Agent):
    """Class representing a nation in the simulation with population and food resource management."""

    def __init__(self, model, country, population, food, food_production, growth_rate, carrying_capacity):
        """
        Args:
            model: The world model (WorldModel)
            country: Name of the nation
            population: Initial population count
            food: Initial food stock
            food_production: Annual food production
            growth_rate: Population growth rate
            carrying_capacity: Maximum population capacity
        """
        super().__init__(model)

        self.country = country
        self.population = population
        self.food = food
        self.food_production = food_production
        self.growth_rate = growth_rate
        self.carrying_capacity = carrying_capacity
        self.pop_history = [population]
        self.food_history = [food]
        self.war_count = 0
        self.famine_count = 0
    def step(self):
        """Simulate one time step (one year)."""
        # Calculate available food (each person consumes CONSUMPTION_PER_PERSON units)
        consumption = self.pop_history[-1] * CONSUMPTION_PER_PERSON
        weather_factor = random.uniform(0.8,1.2)
        actual_production = self.food_production*weather_factor
        self.food = self.food_history[-1] + actual_production - consumption

        if self.food >= 0:
            # Normal population growth using Logistic equation and RK4
            self.population = solve_rk4(
                self.population,
                TIME_STEP,
                self.growth_rate,
                self.carrying_capacity
            )
            self.move()
        else:
            # Famine: population decline based on food shortage
            deficit_per_person = abs(self.food) / self.pop_history[-1]
            death_rate = min(1.0, deficit_per_person * FAMINE_INTENSITY_COEFFICIENT)
            deaths = int(self.pop_history[-1] * death_rate)
            self.population = max(0, self.pop_history[-1] - deaths)
            self.food = 0
            self.famine_count +=1 
            

        # Attempt warfare
        neighbor = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        enemies = [a for a in neighbor if a.population > 0]
        # self.model.grid.get_neighbors(الموقع_الحالي, moore=True, include_center=False)
        if len(enemies) > 0 and random.random() < WARFARE_PROBABILITY:
            enemy = random.choice(enemies)
            if self.population > enemy.population:
                self.attack(enemy)

        # Record historical data
        self.food_history.append(self.food)
        self.pop_history.append(self.population)
    def receive_damage(self, amount):
        """Reduce population due to warfare."""
        self.population = max(0, self.population - self.population*amount)

    def attack(self, enemy):
        """Launch an attack on an enemy nation."""
        enemy.receive_damage(ENEMY_DAMAGE)
        enemy.war_count += 1
        self.receive_damage(ATTACKER_DAMAGE)
        self.war_count += 1 
