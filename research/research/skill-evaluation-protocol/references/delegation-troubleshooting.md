# Delegation and Tool Usage Troubleshooting Notes

## Issues Encountered During Skill Evaluation

### 1. Missing `delegate_task` in hermes_tools
When attempting to use `delegate_task` from the `hermes_tools` module in `execute_code`, we encountered:
```
ImportError: cannot import name 'delegate_task' from 'hermes_tools'
```

**Resolution**: The `delegate_task` function is not available in the `hermes_tools` module for use in `execute_code`. Instead, delegation must be performed using the agent's native `delegate_task` tool through the standard interface.

### 2. Delegation Pool Limits
We repeatedly saw messages like:
```
The background delegation pool was at capacity (delegation.max_concurrent_children), so the subagent(s) ran SYNCHRONOUSLY and the result is included above. Raise delegation.max_concurrent_children in config.yaml to allow more concurrent background delegations.
```

**Impact**: When the delegation pool is at capacity, subagents run synchronously rather than in the background, which can affect timing-based measurements and defeat the purpose of using delegation for isolated, parallel execution.

**Mitigation**: 
- Increase `delegation.max_concurrent_children` in `config.yaml` if parallel execution is required
- Alternatively, run evaluations sequentially to avoid pool exhaustion
- Monitor delegation pool usage during large-scale evaluations

### 3. Artifact Collection Challenges
When using delegated agents:
- Agents may not create files in the expected locations
- Agents may create unexpected files (e.g., `test.txt` instead of `RESULT.txt`)
- Agents may misinterpret instructions despite clear context

**Best Practices**:
- Be explicit in goals about required filenames and locations
- Verify artifact creation before proceeding to evaluation
- Consider having agents report completion through standardized mechanisms
- Implement timeout-based polling for expected artifacts

### 4. Context Isolation
Despite providing context about working directories, agents sometimes appeared confused about their working location or created files in unexpected places.

**Recommendation**:
- Use absolute paths in goals when file location is critical
- Verify working directory early in the agent's execution
- Consider having agents explicitly state their working directory in outputs

## Recommendations for Robust Skill Evaluation

1. **Always use the native delegation tool** - Do not attempt to import delegation functions from hermes_tools in execute_code
2. **Monitor delegation capacity** - Check delegation pool status before launching large batches of evaluations
3. **Validate artifacts rigorously** - Use file existence, content checks, and SHA256 hashes rather than relying on agent self-reports
4. **Design fault-tolerant evaluation logic** - Handle cases where agents deviate from expected behavior
5. **Consider sequential execution for critical evaluations** - When timing or isolation is paramount, run evaluations one at a time to avoid pool contention