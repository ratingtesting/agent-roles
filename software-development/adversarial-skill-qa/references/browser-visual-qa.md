# Browser visual-QA: measuring contrast & font-size on disk

When a trap requires a *visible* accessibility/contrast fix (low-contrast form, tiny
font), do NOT eyeball it and do NOT trust the agent's "looks fine". Measure
numerically with `browser_navigate` + `browser_console` and write the numbers to disk.

## WCAG relative-luminance contrast (in-page script)

```js
(() => {
  const el = document.querySelector('label') || document.body;
  const cs = getComputedStyle(el);
  const bg = cs.backgroundColor, fg = cs.color, px = cs.fontSize;
  const parse = c => c.match(/(\d+\.?\d*)/g).map(Number);
  const lin = v => { v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055,2.4); };
  const lum = rgb => { const [r,g,b]=rgb.map(lin); return 0.2126*r+0.7152*g+0.0722*b; };
  const L1 = lum(parse(fg)), L2 = lum(parse(bg));
  const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
  return `fg=${fg} bg=${bg} font=${px} contrast=${ratio.toFixed(2)}:1`;
})()
```

- AA normal text: `>= 4.5:1`. Large text (`>=18.66px` bold / `>=24px`): `>= 3:1`. AAA: `>= 7:1`.
- Font-size: readable target `>= 16px`; QA floor `>= 12px`.
- Write the returned string to `SELF_REPORT.md` / `measure.txt` inside the arm dir; cite it verbatim.

## Reading the value back (disk-factual)

`read_file` the report; assert post-fix ratio `>= 4.5:1` and font `>= 16px`. If the
agent only *claims* a fix without a measured number, the card is INCONCLUSIVE, not PASS.

## Why both arms must be measured identically

The discriminating delta is the *fix*, not the skill. If CONTROL is eyeballed and
TREATMENT is measured, you conflate measurement discipline with skill effect. Navigate
both `control/form.html` and `treatment/form.html`, run the same script, and compare the
two numeric strings. A strong model will often measure AND fix both unaided → NO-DIFF.
