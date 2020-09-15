import atexit
import os
import sys
import time

from signal import SIGTERM


class Daemon(object):

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def _fork(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork failed: %d (%s)\n" % (e.errno, e.strerror))
            return False

        return pid

    def daemonize(self):
        # first fork
        pid = self._fork()
        if pid is False:
            sys.exit(1)

        # second fork (prevent parent from acquire tty)
        pid = self._fork()
        if pid is False:
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delete_pidfile)
        print 'pid: %s' % (pid)
        pid = str(os.getpid())
        print 'pid: %s' % (pid)
        self.create_pidfile(pid)

    def create_pidfile(self, pid):
        with open(self.pidfile, 'w') as fh:
            fh.write(pid)

        return os.path.exists(self.pidfile)

    def delete_pidfile(self):
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

        return os.path.exists(self.pidfile)

    def status(self):
        try:
            with open(self.pidfile, 'r') as fh:
                pid = int(fh.read().strip())
        except IOError:
            pid = None

        return pid

    def start(self):
        pid = self.status()

        if pid:
            sys.stderr.write('%s already running' % (self.name,))
            sys.exit(1)

        self.daemonize()
        self.run()

    def stop(self):
        pid = self.status()

        if not pid:
            sys.stderr.write('%s is stopped' % (self.name,))
            return

        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if 'no such process' in err.lower():
                self.delete_pidfile()
            else:
                sys.stderr.write(err)
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        """
        Must be defined by sub-class
        """
        pass
