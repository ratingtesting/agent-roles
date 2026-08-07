"""Three-stage viability probe for a recommended dependency (gate 2, step 2a).

COPY THIS FILE and fill in the three stages for the package under test. Run it with the
ISOLATED venv interpreter, not the agent's own:

    PYTHONPATH= .venv/Scripts/python.exe probe_dependency.py     # Windows
    PYTHONPATH= .venv/bin/python probe_dependency.py             # POSIX

Why a file and not `python -c "..."`: inline script flags trip the script-execution approval
gate on some runtimes. A file runs unattended, is re-runnable, and is readable evidence.

Why three separate stages: the stage that fails IS the diagnosis.
  - import fails      -> wrong package name, broken install, or a hard runtime incompatibility
  - construct fails   -> the documented entry point is wrong (classic: empty top-level
                         __init__.py, real API lives in a submodule -> `from pkg import pkg`)
  - execute fails     -> the library installs and constructs but cannot do the actual job

Exit code 0 == PROBE_OK. Non-zero == PROBE_FAIL, and stdout names the stage.
"""
import sys
import traceback

# --- FILL IN ----------------------------------------------------------------
PACKAGE = "PACKAGE_NAME"          # import name (may differ from the pip name)
# ---------------------------------------------------------------------------


def stage_import():
    """Stage 1: import the package. Return the module object."""
    # FILL IN. If the top-level package is empty, the real API is often a submodule:
    #     from PACKAGE import PACKAGE as mod; return mod
    import importlib

    return importlib.import_module(PACKAGE)


def stage_construct(mod):
    """Stage 2: build the main entry object. Return it."""
    # FILL IN, e.g.:  return mod.MainClass()
    raise NotImplementedError("fill in stage_construct")


def stage_execute(obj):
    """Stage 3: perform the most trivial REAL operation. Return something printable."""
    # FILL IN, e.g.:  return obj.do_the_thing("smallest valid input")
    raise NotImplementedError("fill in stage_execute")


def main():
    print("python:", sys.version.split()[0])

    stages = (("import", stage_import), ("construct", stage_construct), ("execute", stage_execute))
    carried = None
    for name, fn in stages:
        try:
            carried = fn() if carried is None and name == "import" else fn(carried)
        except Exception:
            print("{}: FAIL".format(name))
            traceback.print_exc()
            print("PROBE_FAIL: {}".format(name))
            return 1
        detail = getattr(carried, "__file__", None) if name == "import" else carried
        print("{}: OK".format(name), detail if detail is not None else "")

    print("PROBE_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
