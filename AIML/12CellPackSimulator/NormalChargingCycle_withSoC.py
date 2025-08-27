import pybamm
import numpy as np
import pandas as pd
import json

# Constants
BATTERY_CAPACITY_AH = 5.0  # Cell capacity in Ah
INITIAL_SOC = 0.2          # Starting SoC (20%)

# Load model and simulate
model = pybamm.lithium_ion.DFN()
param = model.default_parameter_values
sim = pybamm.Simulation(model, parameter_values=param)
sim.solve([0, 3600])  # 1 hour

# Extract data
t = sim.solution["Time [s]"].entries
voltage = sim.solution["Terminal voltage [V]"].entries
temperature = sim.solution["X-averaged cell temperature [K]"].entries
current = sim.solution["Current [A]"].entries

# Compute SoC manually
delta_t = np.diff(t, prepend=0)  # time step in seconds
cumulative_charge_as = np.cumsum(current * delta_t)  # amp-seconds
cumulative_charge_ah = cumulative_charge_as / 3600   # convert to Ah

estimated_soc = INITIAL_SOC + (cumulative_charge_ah / BATTERY_CAPACITY_AH)
estimated_soc = np.clip(estimated_soc, 0.0, 1.0)  # Limit to 0–1

# Export data
data = []
for i in range(len(t)):
    data.append({
        "time_s": float(t[i]),
        "voltage_v": float(voltage[i]),
        "temperature_k": float(temperature[i]),
        "current_a": float(current[i]),
        "soc": float(round(estimated_soc[i], 4))
    })

# Save to JSON
with open("normal_charging_output_with_soc.json", "w") as f:
    json.dump(data, f, indent=4)

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("normal_charging_output_with_soc.csv", index=False)

print("✅ Simulation complete. SoC calculated manually and saved to:")
print("- normal_charging_output_with_soc.json")
print("- normal_charging_output_with_soc.csv")
