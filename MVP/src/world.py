from mesa import Model
from MVP.src.nation import NationAgent



class WorldModel(Model):
    """World model - manages all nations and the simulation."""

    def __init__(self):
        """Initialize the model and create the three initial nations."""
        super().__init__()
        print("\n--- Starting Simulation ---")
        NationAgent(
            self,
            "ANation_A",
            population=4,
            food=500,
            food_production=1000,
            growth_rate=0.02,
            carrying_capacity=500
        )
        agent = self.agents[-1]
        print(f"{agent.country}: Population={agent.population}, Food={agent.food}")
        NationAgent(
            self,
            "BNation_B",
            population=1500,
            food=700,
            food_production=1600,
            growth_rate=0.025,
            carrying_capacity=700
        )
        agent = self.agents[-1]
        print(f"{agent.country}: Population={agent.population}, Food={agent.food}")
        NationAgent(
            self,
            "CNation_C",
            population=80,
            food=400,
            food_production=1200,
            growth_rate=0.015,
            carrying_capacity=40
        )
        agent = self.agents[-1]
        print(f"{agent.country}: Population={agent.population}, Food={agent.food}")
        print("---------------------------\n")



    def step(self):
        """Execute one simulation step - each nation takes its turn."""
        self.agents.shuffle_do("step")



    def print_summary(self):
        """

        summary events for each nation        :param self:
        """
        print("\n" + "=" * 70)
        print(f"{'SIMULATION SUMMARY':^70}")
        print("=" * 70)
        print(f"{'Nation':<15} {'Population':<15} {'Status':<10} {'Famines':<10} {'Food':<10} {'Wars':<10}")
        print("-" * 70)
        for agent in self.agents:
            status = "Alive" if int(agent.population) > 0 else "Extinct"
            print(f"{agent.country:<15} {int(agent.population):<15,} {status:<10} {agent.famine_count:<10} {int(agent.food_history[-1]):<10} {agent.war_count:<10}")
        print("=" * 70 + "\n")
