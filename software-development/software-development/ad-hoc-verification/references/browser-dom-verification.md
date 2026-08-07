# Browser-DOM Verification for Frontend Deliverables

## When this is the right shape

The deliverable is a page (single-file `index.html`, a static bundle, a prototype) with no test
runner, no build step, and no suite for the gate to detect. The importlib/subprocess templates in
SKILL.md do not apply — the runtime is a browser, and the only honest evidence is **assertions
against the rendered DOM**.

Same discipline as every other ad-hoc case: exercise the changed behavior, get a machine-checkable
result, report it as `ad-hoc verification passed` — never as "tests pass".

## The rule that makes this verification instead of vibes

**Report the number, not the impression.** "Contrast looks fine", "text reads OK", "buttons seem
big enough" are not findings — the eye cannot judge a threshold, so a qualitative pass silently
becomes "no issue" and the defect ships. A check without its measured value is inconclusive.

Read every value from **computed styles on the rendered node**, never from the source. The entire
point is catching cases where the stylesheet did not do what it appears to say (see the `font`
shorthand trap below).

| Metric | Threshold | Source |
|---|---|---|
| Horizontal overflow | `scrollWidth <= innerWidth` | report both |
| Text contrast | ≥ 4.5:1 (≥ 3:1 for ≥24px) | WCAG formula on computed colors |
| Smallest rendered font | ≥ 12px (aim ≥16px for older/low-vision users) | leaf-node sweep |
| Smallest tap target | ≥ 24×24px WCAG 2.2 AA (aim 44×44) | `getBoundingClientRect()` |
| Live region wiring | `role` + `aria-live` present | `getAttribute` |
| Field ↔ hint/error wiring | `aria-describedby` resolves to real ids | `getAttribute` |

## Two constraints on every console expression

**1. Return a string primitive.** Objects and JSON tend to serialize as `null`. Build the answer
as concatenated `'key=' + value` segments joined by `' | '`, then parse the returned string.

**2. Keep it on one line.** Multi-line IIFEs frequently fail with
`SyntaxError: Unexpected end of input`. A single-line `(function(){ ... })()` is reliable and still
gives you loops and helpers. When an expression fails to parse, **collapse it to one line before
assuming the logic is wrong** — that was the actual fix twice in one session.

### Contrast ratio

```js
(function(){var L=function(c){var r=c.map(function(v){v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return 0.2126*r[0]+0.7152*r[1]+0.0722*r[2]};var R=function(a,b){var x=L(a),y=L(b),h=Math.max(x,y),l=Math.min(x,y);return ((h+0.05)/(l+0.05)).toFixed(2)};return 'body=' + R([18,32,58],[244,246,251]) + ' | err=' + R([138,15,24],[253,236,238]);})()
```

Feed it triples parsed from `getComputedStyle(el).color` via `s.match(/\d+/g)`. A `transparent`
or translucent background resolves against an ancestor — pass the ancestor's painted color, not
`rgba(0,0,0,0)`, or the ratio is fiction.

### Smallest-font sweep — exclude visually-hidden text

A naive sweep returns the `.sr-only` node, which is *deliberately* tiny and clipped. That false
positive masks the real smallest visible text. Filter it, and only consider rendered leaf nodes:

```js
(function(){var e=document.querySelectorAll('body *'),m=999,n='';for(var i=0;i<e.length;i++){var t=e[i].textContent;if(e[i].children.length===0&&t&&t.trim()&&e[i].offsetParent!==null&&!/sr-only|visually-hidden/.test(e[i].className)){var f=parseFloat(getComputedStyle(e[i]).fontSize);if(f<m){m=f;n=e[i].className||e[i].tagName}}}return 'minFont='+m+'px('+n+')';})()
```

Always report the offending node's class with the number — you need to know what to fix.

### Tap targets — measure the real hit area

For a radio/checkbox inside a `<label>`, the input may be 26×26 while the clickable label is
718×71. Measuring the input alone produces a **false failure**. Measure whatever ancestor actually
receives the click (`el.closest('label')`) and state which box you measured.

## Defect classes that only measurement finds

### `font:` shorthand silently discards the entire declaration

```css
font: 700 1.35rem/1 inherit;   /* INVALID — whole declaration dropped, no console error */
```

`inherit` is not legal as the family inside the `font` shorthand, so the browser rejects the
**whole rule** and the element falls back to inherited sizing. Observed: a button intended at
1.35rem rendered at 13.3px. The CSS read as correct, and the accessibility snapshot showed nothing.
Only the computed-font sweep caught it.

```css
font-family: inherit; font-weight: 700; font-size: 1.5rem; line-height: 1;   /* correct */
```

Generalized: **an invalid value anywhere in a shorthand kills the whole shorthand.** When a
computed style disagrees with the source, suspect a rejected declaration *before* suspecting
specificity, and confirm with `getComputedStyle`, not by rereading the CSS.

### Stale `aria-live` status carried into the next interaction

A success message left in a `role="status"` region stays announced after the form resets, so it
describes a submission the user is no longer making — screen-reader users get a confidently wrong
status. Clear it when a new attempt starts, guarded so an in-flight message survives:

```js
if (!sending && statusBox.textContent.trim() !== '') { setStatus(''); }
```

Single-shot assertions cannot see this. It requires a **second pass** through the flow.

### Flex child overflowing its row

An input beside a fixed-width button can push past the shared right edge, because flex items
default to `min-width:auto` and refuse to shrink below content size. Assert numerically by
comparing `getBoundingClientRect().right` against a sibling field rather than eyeballing; fix with
`min-width:0` on the flexible child.

## When a ref click doesn't reach the handler

If `browser_click` on a ref leaves state unchanged, do **not** conclude the feature is broken —
dispatch natively and re-check:

```js
document.getElementById('submit-btn').click();
document.getElementById('my-form').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
```

Native `.click()` also lets you chain *set inputs → submit → assert* in a single expression, which
is the efficient way to cover several validation cases per call. Use real `ref` interactions for
the primary path (they exercise the true user route); reach for native dispatch for determinism
and batching. With a mocked `setTimeout` submit, the in-flight and settled messages must be
asserted in **separate** calls.

## Sequence

1. `browser_navigate`
2. `browser_snapshot` — roles, names, grouping, labels (the a11y tree is authoritative here)
3. `browser_console` — attribute detail + all numeric metrics, as concatenated strings
4. Drive the flows — invalid submit, valid submit, and a **re-entry pass after success**
5. `browser_vision` — catches what no assertion was written for: overlap, truncation, stale visible
   state, misalignment. This is what surfaced the stale success message in-session.
6. Re-verify after each fix, and **bust the `file://` cache with a changed query string**
   (`index.html?v=2`) — otherwise you re-measure the pre-fix render and "confirm" a fix that never
   landed. This is the browser analogue of the stale-artifact traps elsewhere in this skill.

Steps 3 and 5 are complementary, not redundant: the numeric sweep finds threshold violations the
eye cannot judge; the visual pass finds state and layout defects nobody thought to assert.

## Reporting

Frame it honestly, with the numbers inline:

- ✅ "Ad-hoc browser verification: contrast 15.0:1 / 8.5:1 / 11.2:1, min font 15.2px, min tap
  52×52px, no horizontal overflow (1249 ≤ 1264), error path focuses first invalid field."
- ❌ "Accessibility verified." / "WCAG compliant." — overstates a spot check into an audit.

State what was **not** covered (real assistive-technology testing, other browsers, zoom levels).
A measured sweep is strong evidence, not a conformance claim.
