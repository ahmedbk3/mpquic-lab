import csv
from pathlib import Path
from collections import Counter

RESULTS = Path("/lab/results")
OUTPUT = RESULTS / "final" / "baseline_A_final.csv"

FILE_SIZE = 50 * 1024 * 1024

loss_levels = {
    "dual-fiber": [0, 1, 2, 5],
    "eth-wifi": [1, 2, 5],
    "sat-terr": [1, 2, 5],
    "cellular": [1, 2, 5],
    "adsl": [1, 2, 5],
}

final_rows = []
seen = Counter()

# Read the main experiment dataset
with open(RESULTS / "baseline_A.csv", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        scenario = row["scenario"]
        index = seen[scenario]
        seen[scenario] += 1

        # Identify the loss level from the five-run batch
        if scenario == "eth-wifi" and index >= 15:
            loss = 5  # Successful replacement run
        else:
            loss = loss_levels[scenario][index // 5]

        if scenario == "eth-wifi" and index == 15:
            row["run"] = "3"
        if row["complete"].strip() != "True":
            continue

        if int(row["bytes"]) != FILE_SIZE:
            continue

        final_rows.append({
            **row,
            "loss_pct": loss,
            "source_file": "baseline_A.csv"
        })

# Add the four remaining 0% baseline scenarios
with open(RESULTS / "baseline_A_noloss.csv", newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        if row["scenario"] == "dual-fiber":
            continue

        if row["complete"].strip() != "True":
            continue

        if int(row["bytes"]) != FILE_SIZE:
            continue

        final_rows.append({
            **row,
            "loss_pct": 0,
            "source_file": "baseline_A_noloss.csv"
        })

# Write consolidated dataset
fields = [
    "timestamp", "scenario", "loss_pct", "run",
    "bytes", "seconds", "mbps", "complete", "source_file"
]

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(final_rows)

# Validate measurements per condition
counts = Counter(
    (row["scenario"], row["loss_pct"])
    for row in final_rows
)

print("\nMeasurements per condition:")
for scenario in loss_levels:
    for loss in [0, 1, 2, 5]:
        print(f"{scenario:12} | {loss}% loss | {counts[(scenario, loss)]} runs")

print(f"\nTotal valid measurements: {len(final_rows)}")
print(f"Output: {OUTPUT}")
