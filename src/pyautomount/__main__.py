import argparse
import json
import os
import pyudev
import re
import subprocess
import sys
import time


def mount(dev, name):
    mount_point = '/media/%s' % (name)
    cmd = ["mount", "-t", "auto", dev, mount_point]
    cmd = ["udisks", "--mount", dev]
    p = subprocess.Popen(
        cmd,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE
    )

    time.sleep(1.5)

    if not os.path.ismount(mount_point):
        out, err = p.communicate()
        return 'mount %s failed %s (%s)' % (name, out, err)

    return True


def unmount(dev, name):
    mount_point = '/media/%s' % (name)
    cmd = ["umount", mount_point]
    cmd = ["udisks", "--unmount", dev]
    p = subprocess.Popen(
        cmd,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE
    )

    time.sleep(1.5)

    if os.path.ismount(mount_point):
        out, err = p.communicate()
        return 'unmount %s failed %s (%s)' % (name, out, err)

    return True


class AutoMount(object):

    def __init__(self, rules=None):
        self.rules = rules or {}
        self.interval = 30

    def match_rules(self, device):
        if not self.rules:
            return False

        match = False
        for rule in self.rules:
            for k, v in rule.items():
                m = re.search(v, device.properties.get(k, ''))
                if not m:
                    break
            else:
                sys.stdout.write('matched %s\n' % (rule,))
                return True

        return match

    def handler(self, device):
        action = device.action
        dev_links = device.properties['DEVLINKS']
        dev_name = device.properties['DEVNAME']
        label = device.properties['ID_FS_LABEL']

        if action == 'add':
            if self.match_rules(device):
                result = mount(dev_name, label)
                if result is True:
                    sys.stdout.write('mounted %s\n' % (dev_name,))
                else:
                    sys.sterr.write(result)

                return

        if action == 'remove':
            if self.match_rules(device):
                result = unmount(dev_name, label)
                if result is True:
                    sys.stdout.write('unmounted %s\n' % (dev_name,))
                else:
                    sys.sterr.write(result)

                return

    def start_monitor(self):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem='block')
        observer = pyudev.MonitorObserver(
            monitor,
            callback=self.handler,
            name='monitor-observer'
        )
        observer.start()

        while True:
            time.sleep(self.interval)


def main():
    rules = {}
    parser = argparse.ArgumentParser()
    parser.add_argument('--rules', help='rules', default=None)
    args = parser.parse_args()

    if args.rules:
        try:
            data = open(args.rules, 'r').read()
            rules = json.loads(data).get('rules', {})
            sys.stdout.write('read rules %s\n' % (args.rules))
        except IOError:
            sys.stderr.write('could not load rules file %s\n', args.rule)

    a = AutoMount(rules=rules)
    a.start_monitor()