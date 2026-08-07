# Ad-hoc jscpd anti-erosion verification

Observed in control 2.5 anti-erosion / reuse ladder session.

## Canonical workflow that worked on Windows/MSYS

1. Create the deliberately duplicated target file.
2. Capture jscpd output into a temp artifact:
   `jscpd <file> > pre-<tool>.txt 2>&1`
3. Apply the refactor/extract-function change.
4. Run:
   `cp <file> <file>.refactored && cat > <file> << 'EOF' ... EOF && jscpd <file> > post-<tool>.txt 2>&1 && rm -f <file>.refactored`
   This avoids a transient jscpd run on the unfinished file if the heredoc succeeds but
   the refactor fails mid-Write. It also gives a deterministic no-backup baseline.
5. Capture both outputs as evidence.
6. Clean up or preserve alongside a README for auditability.

## jscpd quirk to record

jscpd reports `0 (0.00%)` intra-file on this pattern because copy-paste detection is
cross-file by default. Still worth running because:
- It proves no cross-file clones leaked.
- The README should contain an analytical intra-file duplication estimate to explain the
  pre/post behavioral step change.

## Windows/MSYS path/popen notes

- Use `cd /c/Users/...` and `/c/...` paths inside MSYS bash heredocs.
- `cp`, `rm`, heredocs work under `terminal` bash on Windows. Avoid `mv`/`cp -R` outside
  the MSYS translation layer.

## Ad-hoc technique captured by `ad-hoc-verification`

After producing pre/post artifacts, the verification-gate pattern was satisfied by a
separate stdlib-only temp script under `%TEMP%\hermes-verify-<name>.py` that asserted:
- Required helper exists (`_build_message`)
- Public wrappers exist and have expected names
- Each wrapper returns the correct role and forwards name/text

This temp script pattern is already documented in `ad-hoc-verification`; this note is the
external-tool variant of it.
