#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if 'data-ui-skin="wol"' in t and "#cbi-wol" in t:
    print("SKIP  wol.js: already skinned")
    raise SystemExit(0)
old = "\t\treturn m.render();\n\t},"
if old not in t:
    raise SystemExit("wol.js: return m.render() anchor not found")
css_lines = [
"#cbi-wol {",
"	--wol-accent: #5e72e4;",
"	--wol-ok: #2dce89;",
"	--wol-warn: #fb6340;",
"	--wol-border: #e9ecef;",
"	--wol-muted: #8898aa;",
"	--wol-text: #32325d;",
"	--wol-card: #fff;",
"	--wol-soft: #f7f9fc;",
"}",
"#cbi-wol.cbi-section, #cbi-wol .cbi-section {",
"	padding: 0; border: 0; background: none; box-shadow: none; margin: 0 0 16px;",
"}",
'body[theme="dark"] #cbi-wol {',
"	--wol-border: #3a3a3d; --wol-muted: #9aa2ad; --wol-text: #d7dae0;",
"	--wol-card: #232324; --wol-soft: #2b2b2d;",
"}",
"@media (prefers-color-scheme: dark) {",
'	body[theme="normal"] #cbi-wol {',
"		--wol-border: #3a3a3d; --wol-muted: #9aa2ad; --wol-text: #d7dae0;",
"		--wol-card: #232324; --wol-soft: #2b2b2d;",
"	}",
"}",
"#cbi-wol > h2 {",
"	margin: 0 0 6px; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--wol-text);",
"}",
"#cbi-wol .cbi-map-descr {",
"	margin: 0 0 16px; font-size: 13px; line-height: 1.6; color: var(--wol-muted);",
"}",
"#cbi-wol .wol-head {",
"	display: flex; align-items: baseline; justify-content: space-between; gap: 8px 16px; flex-wrap: wrap;",
"	margin: 0 0 16px; padding: 16px 22px; background: var(--wol-card); border: 1px solid var(--wol-border);",
"	border-radius: 12px; box-shadow: 0 2px 12px rgba(50, 50, 93, .06);",
"}",
"#cbi-wol .wol-head > h2 {",
"	margin: 0; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--wol-text);",
"}",
"#cbi-wol .wol-head > .cbi-map-descr {",
"	margin: 0 0 0 auto; font-size: 13px; line-height: 1.6; color: var(--wol-muted); text-align: right;",
"}",
"#cbi-wol .cbi-section-node {",
"	background: var(--wol-card); border: 1px solid var(--wol-border); border-radius: 12px;",
"	box-shadow: 0 2px 12px rgba(50, 50, 93, .06); padding: 16px 18px;",
"}",
"#cbi-wol .cbi-page-actions {",
"	margin-top: 16px; padding: 0; border: 0; background: none;",
"}",
"#cbi-wol .cbi-page-actions .cbi-button {",
"	min-width: 132px; padding: 8px 18px; border-radius: 8px; font-size: 14px;",
"}",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)
new = (
    "\t\treturn m.render().then(function(node) {\n"
    "\t\t\tnode.setAttribute('id', 'cbi-wol');\n"
    "\t\t\tvar css = '' +\n"
    + css_js + ";\n"
    "\t\t\tvar skin = function() {\n"
    "\t\t\t\tvar h2 = null, descr = null, kids = node.children, i;\n"
    "\t\t\t\tfor (i = 0; i < kids.length; i++) {\n"
    "\t\t\t\t\tif (!h2 && kids[i].tagName === 'H2')\n"
    "\t\t\t\t\t\th2 = kids[i];\n"
    "\t\t\t\t\telse if (!descr && kids[i].classList && kids[i].classList.contains('cbi-map-descr'))\n"
    "\t\t\t\t\t\tdescr = kids[i];\n"
    "\t\t\t\t}\n"
    "\t\t\t\tif (h2 && descr && !node.querySelector('.wol-head')) {\n"
    "\t\t\t\t\tvar head = document.createElement('div');\n"
    "\t\t\t\t\thead.className = 'wol-head';\n"
    "\t\t\t\t\tnode.insertBefore(head, h2);\n"
    "\t\t\t\t\thead.appendChild(h2);\n"
    "\t\t\t\t\thead.appendChild(descr);\n"
    "\t\t\t\t}\n"
    "\t\t\t\tif (!node.querySelector('style[data-ui-skin=\"wol\"]'))\n"
    "\t\t\t\t\tnode.insertBefore(E('style', { 'data-ui-skin': 'wol' }, [ css ]), node.firstChild);\n"
    "\t\t\t};\n"
    "\t\t\tskin();\n"
    "\t\t\treturn node;\n"
    "\t\t});\n"
    "\t},"
)
t2 = t.replace(old, new, 1)
if t2 == t:
    raise SystemExit("wol.js: replace failed")
for must in ("#cbi-wol", 'data-ui-skin="wol"', "wol-head", "handleWakeup", "#maincontent .cbi-map", "Wake up host", "callHostHints"):
    if must not in t2:
        raise SystemExit(f"wol.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    wol.js skinned ({p})")
