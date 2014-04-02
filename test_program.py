from corredor.strategy import PingPong

transport = PingPong()

tests = ['test/foo', 'test/bar', 'test/baz']
transport.send_tests(tests)
