import pybamm
import json
import csv
import random

# Configuration
NUM_CELLS = 12
model = pybamm.lithium_ion.SPMe()
parameter_values = pybamm.ParameterValues("Marquis2019")

# Use standard current profile
parameter_values.update({"Current function [A]": 1.5})
sim = pybamm.Simulation(model, parameter_values=parameter_values)
sim.solve([0, 3600])  # 1 hour

solution = sim.solution
time_sec = solution["Time [s]"].entries
time_hr = time_sec / 3600
base_voltage = solution["Terminal voltage [V]"].entries
temperature = solution["X-averaged cell temperature [K]"].entries - 273.15

# Simulate per-cell voltages with slight variance
cell_voltages = []
for _ in range(NUM_CELLS):
    noise = [random.uniform(-0.01, 0.01) for _ in base_voltage]
    cell_voltages.append([v + n for v, n in zip(base_voltage, noise)])

# SoC estimation
initial_capacity = 3.2  # Ah
current_applied = 1.5  # A
soc = [100 - (current_applied * t) / (initial_capacity * 3600) * 100 for t in time_sec]
soc = [max(0, min(100, s)) for s in soc]

# SOH dummy (100% throughout)
soh = [100.0 for _ in time_hr]

# Construct output
output_data = []
for i in range(len(time_hr)):
    entry = {
        "time_hr": time_hr[i],
        "pack_voltage": base_voltage[i],
        "temperature_C": temperature[i],
        "SoC_percent": soc[i],
        "SOH_percent": soh[i],
    }
    for cell_id in range(NUM_CELLS):
        entry[f"cell_{cell_id+1}_voltage"] = cell_voltages[cell_id][i]
    output_data.append(entry)

# Export
with open("12cell_pack_output.json", "w") as f_json:
    json.dump(output_data, f_json, indent=2)

with open("12cell_pack_output.csv", "w", newline="") as f_csv:
    writer = csv.DictWriter(f_csv, fieldnames=output_data[0].keys())
    writer.writeheader()
    writer.writerows(output_data)

print("✅ 12-cell pack simulation completed with SoC. Data saved to CSV and JSON.")
