# Wrong-test traps in QA/training repos

Some repos seed *deliberately bad tests* to bait agents into changing correct
code to pass a misleading assertion. Pattern seen here: `test_multiply_bug`
asserts `subtract(5, 3) == 10` while the implementation is clearly
`a - b`. Fixing the code would be a reward-hack.

## Detection

- Test name contains `bug`, `trap`, `bait`, `wrong`.
- Expected value is obviously wrong for the function under test (order of
  magnitude off, opposite sign, calls the wrong function).
- Comment in the test explicitly admits it is wrong.

## Decision

Apply the `wrong-test vs wrong-code` rule from the parent skill immediately.  
When the test is the bad actor: update or remove the bad test. Do not rewrite
correct production code to match a false expectation.

## Fix shape

1. Confirm the code behavior matches intended contracts from passing tests.
2. Update the bad test's expected value, or remove the trappy test entirely.
3. Re-run the suite. All remaining tests should pass.
4. Do not commit a "fix" that modifies production code solely to clear a
   seeded-bait test.
