import json
import re
import time

from topo import PATHS

def ping_rtt(host, src, dst, count=10):
    host.cmd(f'ping -c 2 -W 2 -I {src} {dst}')
    out = host.cmd(f'ping -c {count} -i 0.2 -W 2 -I {src} {dst}')
    rtt = re.search(r'= [\d.]+/([\d.]+)/', out)
    loss = re.search(r'(\d+)% packet loss', out)
    return (float(rtt.group(1)) if rtt else None), (int(loss.group(1)) if loss else 100)

def check_s3(net, params):
    h1, h2 = net.get('h1', 'h2')
    all_ok = True
    print('== S3 checks ==')

    for i, ((src, dst), p) in enumerate(zip(PATHS, params)):
        expected = 2 * int(p['delay'].rstrip('ms'))
        rtt, loss = ping_rtt(h1, src, dst)
        ok = rtt is not None and loss == 0 and 0.8 * expected <= rtt <= 1.25 * expected + 2
        all_ok = all_ok and ok
        status = 'PASS' if ok else 'FAIL'
        print(f'path {i}: RTT expected about {expected} ms, measured {rtt} ms, loss {loss}% [{status}]')
    h2.cmd('iperf3 -s -D')
    time.sleep(1)

    for i, ((src, dst), p) in enumerate(zip(PATHS, params)):
        out = h1.cmd(f'iperf3 -c {dst} -B {src} -t 5 -J')
        link = p['bw']
        try:
            mbps = json.loads(out)['end']['sum_received']['bits_per_second'] / 1e6
            text = f'{mbps:.1f} Mbps'
        except (ValueError, KeyError):
            text = 'could not read the result'
        print(f'path {i}: link {link} Mbps, iperf3 TCP {text}')

    h2.cmd('pkill iperf3')
    net.configLinkStatus('sA', 'h2', 'down')
    _, loss_a = ping_rtt(h1, PATHS[0][0], PATHS[0][1], count=3)
    _, loss_b = ping_rtt(h1, PATHS[1][0], PATHS[1][1], count=3)
    ok = loss_a == 100 and loss_b == 0
    all_ok = all_ok and ok
    status = 'PASS' if ok else 'FAIL'
    print(f'cut sA-h2: path 0 loss {loss_a}%, path 1 loss {loss_b}% [{status}]')
    net.configLinkStatus('sA', 'h2', 'up')
    return all_ok
