import datetime
import os
import pyudev
import re
import subprocess
import sys
import time

from . daemon import Daemon


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


class AutoMount(Daemon):

    def __init__(self, pidfile, rules=None, log=None):
        self.rules = rules or {}
        self.interval = 30
        self.pidfile = pidfile
        self.stdin = '/dev/null'
        self.stdout = self.stderr = '/var/log/pyautomount.log'

        try:
            if log:
                self.log = open(log, 'a')
        except IOError:
            pass

    def log_error(self, m):
        ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        sys.stderr.write('[%s] ERROR: %s' % (ts, m))

    def log_info(self, m):
        ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        sys.stdout.write('[%s] INFO: %s' % (ts, m))

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
                self.log_info('matched %s\n' % (rule,))
                return True

        return match

    def handler(self, device):
        action = device.action
        dev_name = device.properties['DEVNAME']
        label = device.properties['ID_FS_LABEL']

        if action == 'add':
            if self.match_rules(device):
                result = mount(dev_name, label)
                if result is True:
                    self.log_info('mounted %s\n' % (dev_name,))
                else:
                    self.log_error(result)

                return

        if action == 'remove':
            if self.match_rules(device):
                result = unmount(dev_name, label)
                if result is True:
                    self.log_info('unmounted %s\n' % (dev_name,))
                else:
                    self.log_error(result)

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

    def run(self):
        self.start_monitor()
        while True:
            time.sleep(self.interval)
