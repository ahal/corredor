from corredor.strategies import PingPong

transport = PingPong()

tests = ['test/foo', 'test/bar', 'test/baz']
transport.run_tests(tests)
