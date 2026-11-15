# MPQUIC Lab – S3 & S4 Handover

## 1. Project Overview

This package contains the completed work for two stages of the MPQUIC project:

- **S3 – Network Testbed:** Construction, configuration and validation of the Mininet network environment.
- **S4 – Single-Path QUIC Baseline:** Performance evaluation of single-path QUIC under different network scenarios and packet-loss conditions.

The objective of this work is to provide a validated and reproducible network testbed, together with a single-path QUIC reference dataset that can be used to evaluate the future multipath implementation.

The remaining stages are assigned to the rest of the team:

- S5 – Path-lifecycle state machine.
- S6 – Multipath deployment and evaluation.

---

## 2. Package Contents

```text
handover/
│
├── README.md
├── mpquic-lab-s4.tar.gz
│
├── src/
│   ├── topo.py
│   ├── lab.py
│   ├── baseline.py
│   ├── checks.py
│   ├── step1.py
│   ├── step2.py
│   ├── step3.py
│   ├── step4.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── controller/
│       └── l2_switch.py
│
├── controller/
│   └── l2_switch.py
│
└── results/
    ├── baseline_A.csv
    ├── baseline_A_noloss.csv
    │
    ├── s3/
    │   ├── s3_check_adsl.txt
    │   ├── s3_check_cellular.txt
    │   ├── s3_check_dual-fiber.txt
    │   ├── s3_check_eth-wifi.txt
    │   └── s3_check_sat-terr.txt
    │
    ├── logs/
    │   ├── adsl_loss1.log
    │   ├── adsl_loss2.log
    │   ├── adsl_loss5.log
    │   ├── cellular_loss1.log
    │   ├── cellular_loss2.log
    │   ├── cellular_loss5.log
    │   ├── eth-wifi_loss1.log
    │   ├── eth-wifi_loss2.log
    │   ├── eth-wifi_loss5.log
    │   ├── eth-wifi_loss5_replacement.log
    │   ├── sat-terr_loss1.log
    │   ├── sat-terr_loss2.log
    │   └── sat-terr_loss5.log
    │
    └── final/
        ├── baseline_A_final.csv
        ├── s4_statistics.csv
        ├── consolidate.py
        ├── analyze.py
        └── S4_report.md
```

### Main source files

| File | Purpose |
|---|---|
| `topo.py` | Defines the Mininet topology, network scenarios and IP addresses. |
| `lab.py` | Main launcher for the testbed, S3 checks and S4 experiments. |
| `baseline.py` | Implements the single-path Picoquic baseline measurements. |
| `checks.py` | Contains S3 network validation procedures. |
| `controller/l2_switch.py` | OpenFlow Layer 2 switching controller. |
| `step1.py` – `step4.py` | Individual development and validation scripts. |
| `Dockerfile` | Defines the Docker experiment environment. |
| `entrypoint.sh` | Container entrypoint script. |

---

## 3. Experimental Environment

The project uses the following environment:

- Host operating system: Ubuntu virtual machine.
- Containerization: Docker.
- Network emulator: Mininet.
- Virtual switching: Open vSwitch.
- SDN controller: OS-Ken.
- QUIC implementation: Picoquic.
- QUIC executable: `picoquicdemo`.
- Transport protocol: QUIC over UDP.
- Data transfer size: 50 MiB.
- Repetitions: 5 per experimental condition.

### Docker image

The prepared environment is exported as:

`mpquic-lab-s4.tar.gz`

Docker image tag:

`mpquic-lab:s4`

The archive allows teammates to load the prepared environment without rebuilding the image from the Dockerfile.

---

## 4. Loading the Docker Environment

Copy the handover directory to the Ubuntu machine.

Navigate to the directory containing the exported Docker image:

```bash
cd handover
```

Load the image:

```bash
docker load -i mpquic-lab-s4.tar.gz
```

Verify that the image is available:

```bash
docker images | grep mpquic-lab
```

Expected image:

```text
mpquic-lab   s4
```

The Docker image contains the experiment dependencies. The project source files must still be mounted into the container.

---

## 5. Preparing the Project Directory

The experiment launcher expects the source files to be available under `/lab`.

Create a working directory:

```bash
mkdir -p ~/mpquic-lab
```

Copy the source files:

```bash
cp -r handover/src/. ~/mpquic-lab/
```

Create the results directory:

```bash
mkdir -p ~/mpquic-lab/results
```

Copy the provided results:

```bash
cp -r handover/results/. ~/mpquic-lab/results/
```

The resulting project structure should look like:

```text
mpquic-lab/
├── topo.py
├── lab.py
├── baseline.py
├── checks.py
├── step1.py
├── step2.py
├── step3.py
├── step4.py
├── Dockerfile
├── entrypoint.sh
├── controller/
│   └── l2_switch.py
└── results/
    ├── baseline_A.csv
    ├── baseline_A_noloss.csv
    ├── s3/
    ├── logs/
    └── final/
```

Navigate into the project:

```bash
cd ~/mpquic-lab
```

**Important:** Run the Docker commands from this project directory because `$PWD` is mounted into `/lab`.

---

## 6. S3 – Network Testbed

### 6.1 Topology

The testbed contains:

- Two hosts: `h1` and `h2`.
- Two Open vSwitch switches: `sA` and `sB`.
- One SDN controller.
- Two independent network paths between the hosts.

### Path 0

```text
h1-eth0 → sA → h2-eth0
```

IP addresses:

- h1: `10.0.1.1`
- h2: `10.0.1.2`

### Path 1

```text
h1-eth1 → sB → h2-eth1
```

IP addresses:

- h1: `10.0.2.1`
- h2: `10.0.2.2`

Each path is represented by a separate host interface and switch.

Bandwidth, delay and packet loss are configured on the corresponding h1-to-switch link. The switch-to-h2 link is not shaped.

### 6.2 Network Scenarios

Five network scenarios are defined in `topo.py`.

| Scenario | Path 0 BW | Path 0 Delay | Path 1 BW | Path 1 Delay |
|---|---:|---:|---:|---:|
| Dual-fiber | 100 Mbps | 5 ms | 100 Mbps | 8 ms |
| Ethernet-Wi-Fi | 1000 Mbps | 2 ms | 150 Mbps | 12 ms |
| Satellite-terrestrial | 50 Mbps | 25 ms | 100 Mbps | 180 ms |
| Cellular | 30 Mbps | 35 ms | 25 Mbps | 40 ms |
| ADSL | 50 Mbps | 15 ms | 10 Mbps | 45 ms |

These values represent controlled network conditions inside Mininet.

### 6.3 Running S3 Validation

From the project directory:

```bash
docker run --rm -it --privileged \
  -v /lib/modules:/lib/modules \
  -v "$PWD":/lab \
  mpquic-lab:s4 \
  python3 lab.py --check
```

To validate a specific scenario:

```bash
docker run --rm -it --privileged \
  -v /lib/modules:/lib/modules \
  -v "$PWD":/lab \
  mpquic-lab:s4 \
  python3 lab.py --scenario sat-terr --check
```

Available scenarios:

- `dual-fiber`
- `eth-wifi`
- `sat-terr`
- `cellular`
- `adsl`

S3 validation includes:

1. Starting the Mininet topology.
2. Starting the SDN controller.
3. Connecting the Open vSwitch instances.
4. Configuring host IP addresses.
5. Checking connectivity between the hosts on both paths.
6. Verifying the network configuration.

The saved validation logs are located in:

`results/s3/`

---

## 7. S4 – Single-Path QUIC Baseline

### 7.1 Objective

The objective of S4 is to measure the performance of a single QUIC connection over Path 0 under different network conditions.

This baseline provides a reference for comparison with the future multipath implementation.

### 7.2 Implementation

The baseline implementation is located in:

`baseline.py`

It uses Picoquic's `picoquicdemo` executable.

The experiment follows these steps:

1. Start the selected Mininet network scenario.
2. Apply the requested packet-loss percentage to Path 0.
3. Generate a random 50 MiB file.
4. Start the Picoquic server on h2.
5. Initiate a QUIC download from h1.
6. Record the received bytes and transfer duration.
7. Calculate throughput.
8. Repeat the transfer five times.

The client connects to:

`10.0.1.2:4433`

This address belongs to Path 0.

### 7.3 Throughput Calculation

Throughput is calculated using:

```text
Throughput (Mbps) =
    (Received bytes × 8) / Duration (seconds) / 1,000,000
```

A transfer is considered complete when:

```text
Received bytes = 50 × 1024 × 1024
```

Incomplete transfers are excluded from the consolidated statistical dataset.

### 7.4 Experiment Matrix

Five scenarios were tested at four packet-loss levels:

| Packet loss | Repetitions per scenario |
|---|---:|
| 0% | 5 |
| 1% | 5 |
| 2% | 5 |
| 5% | 5 |

Total:

```text
5 scenarios × 4 loss levels × 5 repetitions
= 100 measurements
```

All experiments use a 50 MiB transfer.

Packet loss is applied to Path 0 only.

### 7.5 Running an S4 Experiment

Example: Dual-fiber with 0% packet loss.

```bash
docker run --rm -it --privileged \
  -v /lib/modules:/lib/modules \
  -v "$PWD":/lab \
  mpquic-lab:s4 \
  python3 lab.py \
  --scenario dual-fiber \
  --loss0 0 \
  --quic-baseline \
  --size-mb 50 \
  --runs 5
```

Example: Dual-fiber with 2% packet loss.

```bash
docker run --rm -it --privileged \
  -v /lib/modules:/lib/modules \
  -v "$PWD":/lab \
  mpquic-lab:s4 \
  python3 lab.py \
  --scenario dual-fiber \
  --loss0 2 \
  --quic-baseline \
  --size-mb 50 \
  --runs 5
```

To test another scenario, change the `--scenario` argument.

To change the packet-loss percentage, change `--loss0`.

**Important:** S4 uses single-path Picoquic over Path 0. Path 1 is configured in the topology but is not used by the baseline transfer.

---

## 8. S4 Results

### 8.1 Consolidated Dataset

The final dataset is:

`results/final/baseline_A_final.csv`

It contains 100 valid measurements.

Each record includes:

- Timestamp.
- Scenario.
- Packet-loss percentage.
- Run number.
- Received bytes.
- Transfer duration.
- Throughput.
- Completion status.
- Source dataset.

The original datasets are preserved:

- `results/baseline_A.csv`
- `results/baseline_A_noloss.csv`

The final dataset combines the selected 0% baseline measurements with the 1%, 2% and 5% loss measurements.

The newer dual-fiber 0% batch was selected. The other four scenarios use their historical 0% batches. The older 20 MiB dual-fiber records were excluded.

### 8.2 Statistical Analysis

The statistical results are saved in:

`results/final/s4_statistics.csv`

The analysis includes:

- Number of runs.
- Mean throughput.
- Standard deviation.
- Minimum throughput.
- Maximum throughput.
- Percentage throughput reduction relative to the 0% baseline.

The analysis script is:

`results/final/analyze.py`

It can be executed from the project directory:

```bash
python3 results/final/analyze.py
```

### 8.3 Results Summary

Mean throughput:

| Scenario | 0% Loss | 1% Loss | 2% Loss | 5% Loss |
|---|---:|---:|---:|---:|
| Dual-fiber | 86.29 Mbps | 62.43 Mbps | 54.66 Mbps | 24.89 Mbps |
| Ethernet-Wi-Fi | 783.45 Mbps | 347.33 Mbps | 337.83 Mbps | 123.76 Mbps |
| Satellite-terrestrial | 45.18 Mbps | 22.82 Mbps | 13.35 Mbps | 6.17 Mbps |
| Cellular | 27.30 Mbps | 17.94 Mbps | 13.16 Mbps | 4.97 Mbps |
| ADSL | 45.70 Mbps | 24.67 Mbps | 18.37 Mbps | 8.24 Mbps |

### 8.4 Throughput Reduction

Percentage reduction compared with the corresponding 0% baseline:

| Scenario | 1% Loss | 2% Loss | 5% Loss |
|---|---:|---:|---:|
| Dual-fiber | 27.66% | 36.66% | 71.16% |
| Ethernet-Wi-Fi | 55.67% | 56.88% | 84.20% |
| Satellite-terrestrial | 49.49% | 70.46% | 86.35% |
| Cellular | 34.28% | 51.81% | 81.79% |
| ADSL | 46.02% | 59.81% | 81.97% |

### 8.5 Interpretation

The results show that packet loss has a significant negative impact on single-path QUIC throughput.

Important observations:

- All five scenarios experience throughput degradation as packet loss increases.
- Satellite-terrestrial exhibits the largest reduction at 5% loss, reaching 86.35%.
- Ethernet-Wi-Fi has the highest baseline throughput, but also significant variability under packet loss.
- Dual-fiber exhibits the smallest relative reduction at 5% loss, although throughput still decreases by 71.16%.
- Cellular and ADSL also experience substantial throughput degradation.

These measurements provide a single-path reference for the future multipath evaluation.

---

## 9. Experiment Logs and Data Traceability

The original experiment logs are located in:

`results/logs/`

They contain the output of the packet-loss experiment batches.

The Ethernet-Wi-Fi 5% experiment includes one incomplete run.

The failed measurement is preserved in the original dataset for traceability, but excluded from the final consolidated dataset.

A replacement measurement was performed and documented in:

`results/logs/eth-wifi_loss5_replacement.log`

The replacement is included in the final 100-measurement dataset.

The consolidation script is:

`results/final/consolidate.py`

It produces:

`results/final/baseline_A_final.csv`

The original source CSV files are not modified by the consolidation process.

---

## 10. Experimental Limitations

The following limitations should be considered when interpreting the results:

1. The experiments use a controlled Mininet environment rather than real Internet connections.
2. S4 evaluates single-path QUIC, not multipath QUIC.
3. Only Path 0 is used for the QUIC baseline transfer.
4. Bandwidth, delay and packet loss are applied to the h1-to-switch link. The switch-to-h2 link is unshaped.
5. Ethernet-Wi-Fi measurements under packet loss exhibit relatively high run-to-run variability.
6. The results characterize the configured experimental environment and should not be generalized to all real-world network conditions.

---

## 11. Continuation of the Project

S3 and S4 are completed and handed over.

The following stages remain for the rest of the team.

### S5 – Path-Lifecycle State Machine

The team will implement the path-lifecycle state machine.

The validated topology and network scenarios can be reused for this stage.

### S6 – Multipath Deployment and Evaluation

The team will deploy and evaluate the multipath implementation.

The S4 single-path dataset should serve as the reference when comparing multipath performance.

Future experiments should aim to use comparable:

- Network scenarios.
- Bandwidth and delay configurations.
- Packet-loss levels.
- Transfer sizes.
- Repetition counts.

This will make the comparison between single-path and multipath results more meaningful.

---

## 12. Handover Status

| Stage | Description | Status |
|---|---|---|
| S3 | Network testbed construction and validation | Completed |
| S4 | Single-path QUIC baseline measurements | Completed |
| S5 | Path-lifecycle state machine | Team continuation |
| S6 | Multipath deployment and evaluation | Team continuation |

### Delivered artifacts

- Validated Mininet topology.
- Network scenario configurations.
- OpenFlow controller.
- Docker environment and exported image.
- S3 validation logs.
- S4 experiment implementation.
- Original experiment datasets.
- Experiment execution logs.
- Consolidated 100-measurement dataset.
- Statistical analysis.
- S4 technical report.

**Final handover:** The S3 network infrastructure and S4 single-path QUIC baseline are provided as a reproducible foundation for the remaining MPQUIC project stages.
