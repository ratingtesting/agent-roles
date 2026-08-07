---
name: skill-evaluation-protocol
description: A standardized protocol for conducting A/B tests to measure the impact of a skill on agent behavior.
---
# Skill Evaluation Protocol

A standardized approach for conducting A/B tests to measure the impact of a specific skill or intervention on agent behavior in autonomous tasks.

## Trigger Conditions
Use this protocol when you need to empirically determine whether a given skill (e.g., `keelwright`) produces a measurable difference in agent outputs compared to a control condition, across multiple test scenarios.

## Procedure
1. **Define Test Cases**
   - For each test case, specify:
     - A clear goal/task description.
     - A criterion for difference (what would indicate the skill caused a divergence).
     - Required artifacts (e.g., `RESULT.txt`, logs, file modifications).
   - Ensure the criterion is based on observable evidence (file content, SHA256, tool output), not self-report.

2. **Prepare Directories**
   - For each test ID `X.Y`, create directories:
     - `<RUN_DIR>/X.Y/control/`
     - `<RUN_DIR>/X.Y/treatment/`

3. **Run Control Agent**
   - Context: `"You are working in [control_dir]. [goal]"`
   - Goal: `[goal]\n\nCreate a file RESULT.txt in the current directory describing your approach, decisions, and the final outcome. Include any files you created or modified.`
   - Role: `leaf`
   - Wait for the agent to complete and produce artifacts (e.g., `RESULT.txt`).

4. **Run Treatment Agent**
   - Context: `"You are working in [treatment_dir]. First, load the target skill and references: skill_view(name='skill_name') + references: [list relevant refs]. Then follow the goal: [goal]"`
   - Goal: same as control.
   - Role: `leaf`
   - Wait for the agent to complete and produce artifacts.

5. **Wait for Artifacts**
   - Poll for the expected artifact files (e.g., `RESULT.txt`) in both directories with a timeout (e.g., 30 seconds).
   - If artifacts do not appear within timeout, treat as `INCONCLUSIVE` and note the missing evidence.

6. **Determine Verdict**
   - Compare artifacts based on the pre-defined criterion:
     - If treatment shows the expected difference (per criterion) and control does not → `DISCRIMINATES`.
     - If both show same behavior (both pass or both fail the criterion) → `NO-DIFF`.
     - If one shows partial compliance → `PARTIAL` (if applicable).
     - If artifacts missing or unusable → `INCONCLUSIVE`.
     - If procedural violations (e.g., treatment did not load skill) → `INVALID`.
   - Avoid judging by style or phrasing unless explicitly part of the criterion.

7. **Record Results**
   - Append a JSON line to `<RUN_DIR>/results.jsonl` with:
     ```json
     {
       "run_id": "<RUN_ID>",
       "model": "<model_used>",
       "tier_by_benchmark": "<tier_basis>",
       "sector": <sector_number>,
       "test_id": "<test_id>",
       "verdict": "<VERDICT>",
       "control_fact": "<brief_evidence_from_control>",
       "treatment_fact": "<brief_evidence_from_treatment>",
       "discriminates": <true/false>,
       "self_report_mismatch": <false/true>,
       "api_calls_control": <integer>,
       "api_calls_treatment": <integer>,
       "evidence": "<description_of_evidence>",
       "artifact_path": "<relative_paths_to_artifacts>"
     }
     ```
   - Use evidence from actual file contents, tool outputs, or SHA256 hashes.

8. **Handle Delegation Limits**
   - If delegation reports "background delegation pool at capacity", note that subagents ran synchronously.
   - Consider increasing `delegation.max_concurrent_children` in `config.yaml` for future runs, or run tests sequentially to avoid overload.

9. **Post-Processing**
   - After all tests, generate a summary report (`REPORT.md`) with:
     - Table of all tests and verdicts.
     - Counts of each verdict type.
     - List of any `CANNOT-RUN` or `INVALID` tests with reasons.
     - Links to artifact directories for manual review.

## Pitfalls
- **Subagents do not inherit skills**: Always explicitly include `skill_view(name='skill_name')` in the treatment context; otherwise, the treatment is invalid.
- **Confusing self-report with evidence**: Trust file artifacts, logs, or tool outputs over the agent's verbal claims of success/failure.
- **Premature verdict**: Wait for artifacts to appear; do not judge based on incomplete or missing output.
- **Ignoring delegation pool limits**: Overloading concurrent delegations may cause silent failures or sequential execution, skewing timing-based metrics.
- **Vague criteria**: Define the difference criterion concretely before running tests (e.g., "treatment file contains X, control file does not").

## References
- This protocol adapts principles from the keelwright QA framework (see `keelwright/references/qa-master-prompt.md`).
- For delegation configuration, see Hermes Agent documentation on `delegation.max_concurrent_children`.