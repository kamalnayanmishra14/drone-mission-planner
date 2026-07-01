import json
import matplotlib.pyplot as plt
from mission_planner import generate_lawnmower_path
from dgca_checker import check_compliance
from exporter import export_to_csv

with open("sample_field.json", "r") as f:
    data = json.load(f)

waypoints = generate_lawnmower_path(data)
compliance = check_compliance(waypoints, data)
export_to_csv(waypoints)

print(f"\n--- Mission Execution Summary ---")
print(f"Status: {compliance['status']}")
print(f"Safety Score: {compliance['score']}/100")
print(f"Message: {compliance['reason']}\n")

lats = [w[0] for w in waypoints]
lons = [w[1] for w in waypoints]

plt.figure(figsize=(8, 6))
plt.plot(lons, lats, marker='o', color='b', linestyle='-', label='Drone Path')
plt.title(f"Lawnmower Waypoint Generation - {data['field_name']}")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True)
plt.legend()
plt.show()
