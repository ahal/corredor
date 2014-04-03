"""
Program emulates how the python side of the marionette-js-runner host
might look. Sleeps instead of actually doing the work.
"""

from corredor.strategy import PingPong
import time

transport = PingPong()

# figure out which tests to run
tests = ['test/foo', 'test/bar', 'test/baz']
for test in tests:
    # wait for profile to run
    profile = transport.synchronize('profile')
    # use profile to launch b2g_desktop/device
    time.sleep(1)
    # set up monitoring for timeouts/crashes
    transport.send_test(test)
    # do cleanup
    time.sleep(1)

transport.finish()
