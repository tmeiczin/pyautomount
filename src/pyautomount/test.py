import time

from pyautomount.daemon import Daemon

class Foo(Daemon):

    def run(self):
        while True:
            print 'blah'
            time.sleep(1)

f = Foo('/tmp/foo.pid')
f.start()
