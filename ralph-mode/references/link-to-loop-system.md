# Ralph Mode within the Loop System

## Relationship to execution-loop

Ralph Mode implements Layer 2 (Persistence) of the execution-loop system:
- **Phase 1+2** = planning (same as execution-loop writing-plans + executing-plans)
- **Phase 3** = the building iteration
- **Backpressure gates** = Layer 3 (Stability Check)
- **Hats** = delegate_task spawning (covered by execution-loop Layer 5 spawning pattern)

## When to use Ralph Mode instead of full execution-loop

Use Ralph Mode standalone when the task is a multi-file feature or bugfix that needs:
- Structured iterations with concrete backpressure gates
- Sub-agent delegation with persona hats
- PROGRESS.md logging
- No autoresearch or match loop layers needed

Use the full execution-loop (5 layers) when the task has:
- Critical visual QA (frontend)
- Bounded iterative improvement toward a metric
- Cross-run learning from repeated failures
- Complex stability failure modes beyond "dead retry"

## History

Ralph Mode replaces the 7 PowerShell loop scripts (ralph-init, ralph-cancel, ralph-stop-hook, doubt-gate, task-completion, drift-reanchor, auto-loop) that were removed from ClawHub. The original ClawHub references/scripts.md now returns 404.
