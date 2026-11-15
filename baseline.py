import csv
import os
import shutil
import subprocess
import time

from topo import PATHS

DEMO = '/opt/picoquic/picoquicdemo'
CERT = '/opt/certs/cert.pem'
KEY = '/opt/certs/key.pem'
RESULTS = '/lab/results'

def run_baseline(net, scenario, size_mb, runs):
    h1, h2 = net.get('h1', 'h2')
    os.makedirs('/tmp/www', exist_ok=True)
    os.makedirs(RESULTS, exist_ok=True)

    subprocess.run(['dd', 'if=/dev/urandom', 'of=/tmp/www/data.bin', 'bs=1M', f'count={size_mb}'],
                   check=True, capture_output=True)
    h2.cmd(f'{DEMO} -p 4433 -c {CERT} -k {KEY} -w /tmp/www > /tmp/quic_server.log 2>&1 &')
    time.sleep(1)
    csv_path = os.path.join(RESULTS, 'baseline_A.csv')
    is_new = not os.path.exists(csv_path)

    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(['timestamp', 'scenario', 'run', 'bytes', 'seconds', 'mbps', 'complete'])
        print('== S4 baseline: single-path QUIC over path 0 ==')

        for run in range(runs):
            shutil.rmtree('/tmp/dl', ignore_errors=True)
            os.makedirs('/tmp/dl')
            start = time.time()
            h1.cmd(f'{DEMO} -n test.example.com -o /tmp/dl {PATHS[0][1]} 4433 /data.bin > /tmp/quic_client.log 2>&1')
            seconds = time.time() - start

            received = sum(os.path.getsize(os.path.join('/tmp/dl', name)) for name in os.listdir('/tmp/dl'))
            complete = received == size_mb * 1024 * 1024
            mbps = received * 8 / seconds / 1e6
            writer.writerow([int(time.time()), scenario, run, received, round(seconds, 3), round(mbps, 2), complete])
            status = 'complete' if complete else 'INCOMPLETE, read /tmp/quic_client.log'
            print(f'run {run}: {received} bytes in {seconds:.2f} s = {mbps:.1f} Mbps [{status}]')
    h2.cmd('pkill -f picoquicdemo')

