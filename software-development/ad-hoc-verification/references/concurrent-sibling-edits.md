# Concurrent sibling agent edits

`patch`/`write` can return:
```
"_warning": "... was modified by sibling subagent 'sa-...' at ... after this agent's last read at ... Re-read the file before writing."
```

Multiple agents may edit the same workspace concurrently. When that warning appears, stop and **re-read from disk**, re-derive the change from the current contents, then re-apply and re-run verification.
