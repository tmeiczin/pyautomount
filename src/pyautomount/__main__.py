import argparse
import json
import sys

from . automount import AutoMount


def main():
    rules = {}
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'stop', 'restart'])
    parser.add_argument('--rules', help='rules', default=None)
    parser.add_argument('--log', help='log', default=None)
    parser.add_argument('--pidfile', help='pidfile', default=None)
    args = parser.parse_args()

    pidfile = args.pidfile or '/tmp/pyautomount.pid'

    if args.rules:
        try:
            data = open(args.rules, 'r').read()
            rules = json.loads(data).get('rules', {})
        except IOError:
            sys.stderr.write('could not load rules file %s\n', args.rule)

    a = AutoMount(pidfile, rules=rules, log=args.log)
    f = getattr(a, args.action)
    f()


if __name__ == '__main__':
    main()
