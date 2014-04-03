.. _strategy

Strategy
========

Central to corredor is the concept of a test strategy. Not all test runners run tests in the same way.
For example, some run one test at a time and collect results and perform cleanup in between. Others run
all tests at once and don't collect results until the end. Some test runners can run tests in parallel,
others need to run sequentially.

Corredor provides strategies that correspond to the most popular strategies used in the wild.
