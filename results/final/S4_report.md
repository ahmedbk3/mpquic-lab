# S3 and S4 – Network Testbed and Single-Path QUIC Baseline

## 1. Project scope

This work covers:

- S3: Building and validating the Mininet network testbed.
- S4: Measuring single-path QUIC performance under different network conditions.

The objective of S4 is to establish a baseline that can later be compared with the multipath QUIC implementation.

S5 and S6 are outside the scope of this work and will be handled by the other team members.

## 2. Experimental environment

- Host OS: Ubuntu virtual machine
- Containerization: Docker
- Network emulator: Mininet
- Virtual switches: Open vSwitch
- Controller: OS-Ken
- QUIC implementation: Picoquic (`picoquicdemo`)
- Transport protocol: QUIC over UDP
- Data transfer size: 50 MiB
- Repetitions: 5 per condition
- Docker image: `mpquic-lab:s4`

The Docker image contains the dependencies and tools required to reproduce the testbed.

## 3. Network topology

The testbed contains:

- Two hosts: h1 and h2
- Two switches: sA and sB
- Two independent network paths

### Path 0

h1-eth0 → sA → h2-eth0

- h1: 10.0.1.1
- h2: 10.0.1.2

### Path 1

h1-eth1 → sB → h2-eth1

- h1: 10.0.2.1
- h2: 10.0.2.2

Bandwidth, delay and packet loss are configured on the h1-to-switch link of each path. The switch-to-h2 link is not shaped.

For S4, the QUIC client connects through Path 0 only. Path 1 is present in the topology but is not used by the baseline transfer.

## 4. Network scenarios

The following configurations are defined in `topo.py`.

| Scenario | Path 0 bandwidth | Path 0 delay | Path 1 bandwidth | Path 1 delay |
|---|---:|---:|---:|---:|
| Dual-fiber | 100 Mbps | 5 ms | 100 Mbps | 8 ms |
| Ethernet-Wi-Fi | 1000 Mbps | 2 ms | 150 Mbps | 12 ms |
| Satellite-terrestrial | 50 Mbps | 25 ms | 100 Mbps | 180 ms |
| Cellular | 30 Mbps | 35 ms | 25 Mbps | 40 ms |
| ADSL | 50 Mbps | 15 ms | 10 Mbps | 45 ms |

## 5. S3 – Testbed validation

S3 focused on building and validating the network infrastructure.

Validation included:

- Starting the Mininet topology.
- Connecting the Open vSwitch instances to the controller.
- Configuring host IP addresses.
- Checking connectivity between h1 and h2 on both paths.
- Verifying the network configuration and traffic-control settings.
- Saving validation logs for all five scenarios.

The S3 validation logs are stored in:

`results/s3_check_*.txt`

## 6. S4 – Single-path QUIC baseline

### 6.1 Objective

Measure the performance of a single QUIC connection over Path 0 under different bandwidth, delay and packet-loss conditions.

### 6.2 Methodology

The experiment uses Picoquic's `picoquicdemo`.

1. Start the Mininet topology for the selected scenario.
2. Apply the requested packet-loss percentage to Path 0.
3. Generate a random 50 MiB file.
4. Start the Picoquic server on h2.
5. Download the file from h1 using Path 0.
6. Record the transfer duration and received bytes.
7. Repeat the experiment five times.

The throughput is calculated as:

Throughput (Mbps) = Received bytes × 8 / Duration (seconds) / 1,000,000

A transfer is considered complete when the received file size equals 50 MiB.

### 6.3 Experiment matrix

Five scenarios were tested at four packet-loss levels:

- 0%
- 1%
- 2%
- 5%

This gives:

5 scenarios × 4 loss levels × 5 repetitions = 100 measurements.

All measurements represent single-path QUIC transfers over Path 0.

The 0% measurements were consolidated from the existing baseline datasets. The newer dual-fiber 0% batch was selected, while the 0% measurements for the other four scenarios were taken from the historical baseline dataset.

### 6.4 Results

Mean throughput and reduction relative to the corresponding 0% baseline:

| Scenario | 0% Mbps | 1% reduction | 2% reduction | 5% reduction |
|---|---:|---:|---:|---:|
| Dual-fiber | 86.29 | 27.66% | 36.66% | 71.16% |
| Ethernet-Wi-Fi | 783.45 | 55.67% | 56.88% | 84.20% |
| Satellite-terrestrial | 45.18 | 49.49% | 70.46% | 86.35% |
| Cellular | 27.30 | 34.28% | 51.81% | 81.79% |
| ADSL | 45.70 | 46.02% | 59.81% | 81.97% |

### 6.5 Interpretation

The results show that packet loss has a significant negative impact on single-path QUIC throughput.

Key observations:

- All five scenarios experience throughput degradation as packet loss increases.
- Satellite-terrestrial shows the largest reduction at 5% loss: 86.35%.
- Ethernet-Wi-Fi has the highest baseline throughput, but also considerable run-to-run variability under packet loss.
- Dual-fiber shows the smallest relative reduction at 5% loss, although throughput still decreases by 71.16%.
- Cellular and ADSL also experience substantial throughput degradation.

These results provide a reference for evaluating the behavior of the future multipath implementation.

## 7. Limitations

- These are controlled Mininet experiments, not measurements over real Internet connections.
- S4 uses Picoquic in single-path mode.
- Only Path 0 is used for the QUIC transfer.
- The configured bandwidth, delay and packet loss apply to the h1-to-switch link; the switch-to-h2 link is unshaped.
- The results characterize the tested configuration and should not be generalized to every real-world network.
- Ethernet-Wi-Fi measurements under packet loss show relatively high variability, which should be considered when interpreting averages.

## 8. Reproducibility and project files

Main project files:

- `topo.py`: Network topology and scenario configurations.
- `lab.py`: Main experiment and testbed launcher.
- `checks.py`: S3 validation procedures.
- `baseline.py`: S4 Picoquic baseline implementation.
- `controller/l2_switch.py`: OpenFlow switching controller.
- `step1.py` to `step4.py`: Individual development and validation scripts.
- `Dockerfile`: Docker environment definition.

### Consolidated results

`results/final/baseline_A_final.csv`

Contains 100 valid measurements, including scenario, packet-loss level, throughput, duration and source dataset.

`results/final/s4_statistics.csv`

Contains 20 statistical records with:

- Number of runs
- Mean throughput
- Standard deviation
- Minimum throughput
- Maximum throughput
- Throughput reduction relative to baseline

Original datasets and experiment logs are preserved in the results directory.

## 9. Handover to the team

S3 and S4 are completed.

The team can use the validated topology and S4 results as the starting point for subsequent work:

- S5: Path-lifecycle state machine.
- S6: Multipath deployment and evaluation.

The S4 measurements should serve as the single-path reference when comparing the future multipath implementation.
