import argparse
import os
import subprocess
import sys
import time
from baseline import run_baseline

from mininet.cli import CLI
from mininet.log import setLogLevel

from checks import check_s3
from topo import SCENARIOS, build_network, set_addresses

HERE = os.path.dirname(os.path.abspath(__file__))


def start_controller():
    log = open('/tmp/controller.log', 'w')
    app = os.path.join(HERE, 'controller', 'l2_switch.py')
    proc = subprocess.Popen(['osken-manager', '--ofp-tcp-listen-port', '6653', app],
                            stdout=log, stderr=subprocess.STDOUT)
    time.sleep(3)
    return proc

def main():
    parser = argparse.ArgumentParser(description='Dual-path lab for the MP-QUIC project')
    parser.add_argument('--scenario', choices=list(SCENARIOS), default='dual-fiber')
    parser.add_argument('--loss0', type=float, default=0, help='percent loss on path 0')
    parser.add_argument('--loss1', type=float, default=0, help='percent loss on path 1')
    parser.add_argument('--datapath', choices=['kernel', 'user'], default='kernel')
    parser.add_argument('--check', action='store_true', help='run the S3 checks')

    parser.add_argument('--cli', action='store_true', help='open the Mininet prompt at the end')
    parser.add_argument('--quic-baseline', action='store_true', help='run the S4 baseline')
    parser.add_argument('--size-mb', type=int, default=20)
    parser.add_argument('--runs', type=int, default=3)
    args = parser.parse_args()
    setLogLevel('info')
    controller = start_controller()
    net, params = build_network(args.scenario, args.loss0, args.loss1, args.datapath)
    ok = True
    try:
        net.start()
        net.waitConnected(timeout=15)
        set_addresses(net)
        if args.check:
            ok = check_s3(net, params)
        if args.quic_baseline:
            run_baseline(net, args.scenario, args.size_mb, args.runs)
        if args.cli:
            CLI(net)
    finally:
        net.stop()
        controller.terminate()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
