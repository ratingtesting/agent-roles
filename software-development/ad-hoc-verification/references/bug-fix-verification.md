
Use when Hermes receives a bug-fix control task that demands explicit artifacts: buggy initial code, failing tests, fixed code, passing tests, and persisted pytest output proving the transition.

## Canonical sequence
1. Save buggy code as `*_original.py`
2. Write tests asserting intended behavior
3. Run: `python -m pytest <test_file>.py -v`
4. Save failure transcript, e.g. `pytest_output.txt`
5. Fix the code; save as `*_fixed.py`
6. Run the **same tests** against fixed code
7. Save pass output

## Invariant assertions
Keep assertions identical between buggy and fixed runs. Do not rewrite tests after the patch; that destroys evidence.

## Minimal invocation for fixed code
```bash
cd <control_dir>
python -m pytest test_*_after_fix.py -v
```

## Termination checkpoint
The task is not complete until both the failing run and the passing run have persisted evidence in the control directory.
