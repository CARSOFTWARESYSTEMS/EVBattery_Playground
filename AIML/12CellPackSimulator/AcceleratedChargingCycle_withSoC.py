import pybamm
import json
import csv

# Load model and parameter values
model = pybamm.lithium_ion.SPMe()
parameter_values = pybamm.ParameterValues("Marquis2019")

# Update current function for accelerated charging
def accelerated_current(t):
    return 5  # 5 A constant current (high rate for accelerated charge)

parameter_values.update({"Current function [A]": accelerated_current})

# Setup and run simulation
sim = pybamm.Simulation(model, parameter_values=parameter_values)
sim.solve([0, 3600])  # simulate for 1 hour (3600 seconds)

# Extract results
solution = sim.solution
time_hours = solution["Time [s]"].entries / 3600
voltage = solution["Terminal voltage [V]"].entries
temperature = solution["X-averaged cell temperature [K]"].entries - 273.15  # °C

# SoC computation (based on discharge capacity integration)
initial_capacity = 3.2  # Ah (example, adjust if needed)
current_applied = accelerated_current(0)  # constant current
soc = [100 - (current_applied * t) / (initial_capacity * 3600) * 100 for t in solution["Time [s]"].entries]
soc = [max(0, min(100, x)) for x in soc]  # clamp between 0–100

# Save to JSON and CSV
data = [
    {
        "time_hr": t,
        "voltage_V": v,
        "temperature_C": temp,
        "SoC_percent": s
    }
    for t, v, temp, s in zip(time_hours, voltage, temperature, soc)
]

# JSON
with open("accelerated_charging_output.json", "w") as f_json:
    json.dump(data, f_json, indent=2)

# CSV
with open("accelerated_charging_output.csv", "w", newline="") as f_csv:
    writer = csv.DictWriter(f_csv, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print("✅ Accelerated charging simulation completed. Data saved to CSV and JSON.")
