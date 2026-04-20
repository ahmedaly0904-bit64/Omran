import random
def logistic_derivative(population, growth_rate, carrying_capacity):
    """Calculate the rate of population change using the Logistic equation."""
    return growth_rate * population * (1 - population / carrying_capacity)

def solve_rk4(population, time_step, growth_rate, carrying_capacity):
    """Solve the population equation using 4th-order Runge-Kutta method."""
    k1 = logistic_derivative(population, growth_rate, carrying_capacity)
    k2 = logistic_derivative(population + 0.5 * time_step * k1, growth_rate, carrying_capacity)
    k3 = logistic_derivative(population + 0.5 * time_step * k2, growth_rate, carrying_capacity)
    k4 = logistic_derivative(population + time_step * k3, growth_rate, carrying_capacity)

    population += (time_step / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return population

def stochastic_growth(population, growth_rate , carrying_capacity ,TIME_STEP = 1):
    exact_value = solve_rk4(population, TIME_STEP, growth_rate, carrying_capacity)
    base = int(exact_value)
    fraction = exact_value - base

    # Roll the dice against the fraction (The "Monte Carlo" step)
    if random.random() < fraction:
        return base + 1
    else:
        return base