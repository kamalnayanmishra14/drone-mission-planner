import csv

def export_to_csv(waypoints, filename="mission_route.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Index", "Latitude", "Longitude", "Altitude_M"])
        for idx, wp in enumerate(waypoints):
            writer.writerow([idx, wp[0], wp[1], wp[2]])
    print(f" Saved: {filename}")
