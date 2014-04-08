"""
Program emulates how the python side of the marionette-js-runner host
might look. Sleeps instead of actually doing the work.
"""

from corredor.strategy import PingPong
import time

transport = PingPong()

def launch_target(data):
    profile = data['profile']
    print 'received profile: %s' % profile
    # use profile to launch b2g_desktop/device
    time.sleep(1)
    # send ready
    transport.send_json({'action': 'ready'})

# register callback on profile action
transport.register_action('profile', launch_target)

# figure out which tests to run
tests = ['test/foo', 'test/bar', 'test/baz']
# set up monitoring for timeouts/crashes
transport.send_tests(tests)
transport.finish()
