#!/bin/bash
service openvswitch-switch start >/dev/null 2>&1 || /usr/share/openvswitch/scripts/ovs-ctl start >/dev/null 2>&1
exec "$@"

