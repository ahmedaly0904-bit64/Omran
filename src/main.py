from world import WorldModel
from nation import Nation
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def print_summary(world):
    print("\n" + "=" * 75)
    print(f"{'SIMULATION SUMMARY — Year ' + str(world.year):^75}")
    print("=" * 75)
    print(f"{'Nation':<12} {'Population':<14}"
          f"{'Status':<10} {'Famines':<10} {'Wars':<8}")
    print("-" * 75)
    for n in world.nations:
        status = "Alive" if n.is_alive else "Extinct"
        print(
            f"{n.name:<12} {int(n.population):<14,} "
            f"{status:<10} {n.famine_count:<10} {n.war_count:<8}"
        )
    print("=" * 75 + "\n")

starting_nations = [
            Nation(
                name="Nation_A",
                population=420,
                food=82300,
                food_production=1000,
                growth_rate=0.02,
                carrying_capacity=1000,
            ),
            Nation(
                name="Nation_B",
                population=901,
                food=10000,
                food_production=1600,
                growth_rate=0.025,
                carrying_capacity=2000,

            ),
            Nation(
                name="Nation_C",
                population=802,
                food=40000,
                food_production=1200,
                growth_rate=0.015,
                carrying_capacity=1500,
            ),
        ]

world = WorldModel(starting_nations)
world.run(100)
print_summary(world)
world.display()
colorscale = [
    [0.0,   "grey"],   # ← 0 = فاضي
    [0.33,  "red"],   # ← 1 = Nation_A
    [0.66,  "green"],   # ← 2 = Nation_B
    [1.0,   "blue"],   # ← 3 = Nation_C
]
snapshot = world.get_snapshot()
fig = make_subplots(1,2)
fig.add_trace(go.Heatmap(z=snapshot, colorscale=colorscale),row=1,col=1)
fig.update_yaxes(tickformat="d", title_text="Population", row=1, col=2)

for nation in world.nations:
    fig.add_trace(go.Scatter(

        x=[i for i in range(len(nation.pop_history))],
        y=nation.pop_history,
        name = nation.name,

    ),row= 1,col=2)
fig.update_layout(
    title= 'Map of Nations',
    xaxis_title= 'X-axis',
    yaxis_title= 'Y-axis',
)
fig.show()