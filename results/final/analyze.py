import csv
from collections import defaultdict
from statistics import mean, stdev
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "results/final/baseline_A_final.csv"
OUTPUT = ROOT / "results/final/s4_statistics.csv"

data = defaultdict(list)

with open(INPUT, newline="") as f:
    for row in csv.DictReader(f):
        key = (row["scenario"], int(row["loss_pct"]))
        data[key].append(float(row["mbps"]))

scenarios = ["dual-fiber", "eth-wifi", "sat-terr", "cellular", "adsl"]
loss_levels = [0, 1, 2, 5]

results = []

for scenario in scenarios:
    baseline = mean(data[(scenario, 0)])

    for loss in loss_levels:
        values = data[(scenario, loss)]
        avg = mean(values)

        results.append({
            "scenario": scenario,
            "loss_pct": loss,
            "runs": len(values),
            "mean_mbps": round(avg, 2),
            "std_dev_mbps": round(stdev(values), 2),
            "min_mbps": round(min(values), 2),
            "max_mbps": round(max(values), 2),
            "reduction_pct": round((baseline - avg) / baseline * 100, 2)
        })

fields = [
    "scenario", "loss_pct", "runs", "mean_mbps",
    "std_dev_mbps", "min_mbps", "max_mbps", "reduction_pct"
]

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

print(f"Saved {len(results)} statistical records to {OUTPUT}")

