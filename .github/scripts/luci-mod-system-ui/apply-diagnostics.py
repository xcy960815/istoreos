#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-diagnostics" in t:
    print("SKIP  diagnostics.js: already skinned")
    raise SystemExit(0)

old = "\t\treturn view;\n\t},"
if old not in t:
    raise SystemExit("diagnostics.js: return view anchor not found")

css_lines = [
    "#cbi-diagnostics {",
    "	--dg-accent: #5e72e4; --dg-border: #e9ecef; --dg-muted: #8898aa;",
    "	--dg-text: #32325d; --dg-card: #fff; --dg-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-diagnostics { --dg-border:#3a3a3d; --dg-muted:#9aa2ad; --dg-text:#d7dae0; --dg-card:#232324; --dg-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-diagnostics { --dg-border:#3a3a3d; --dg-muted:#9aa2ad; --dg-text:#d7dae0; --dg-card:#232324; --dg-soft:#2b2b2d; } }',
    "#cbi-diagnostics > h2 { margin:0 0 6px; font-size:18px; font-weight:600; line-height:1.3; color:var(--dg-text); }",
    "#cbi-diagnostics .cbi-map-descr { margin:0 0 16px; font-size:13px; line-height:1.6; color:var(--dg-muted); }",
    "#cbi-diagnostics > table.table {",
    "	display:block; width:100%; box-sizing:border-box;",
    "	background:var(--dg-card); border:1px solid var(--dg-border); border-radius:12px;",
    "	box-shadow:0 2px 12px rgba(50,50,93,.06); padding:18px 20px; margin:0 0 16px;",
    "}",
    "#cbi-diagnostics > table.table tbody, #cbi-diagnostics > table.table .tr {",
    "	display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:14px; width:100%;",
    "}",
    "#cbi-diagnostics > table.table .td {",
    "	display:flex; flex-direction:column; gap:10px; padding:14px; margin:0;",
    "	border:1px solid var(--dg-border); border-radius:10px; background:var(--dg-soft);",
    "	text-align:left;",
    "}",
    "#cbi-diagnostics > table.table .td > input[type=\"text\"],",
    "#cbi-diagnostics > table.table .td > select {",
    "	width:100%; box-sizing:border-box; margin:0 !important; padding:8px 12px;",
    "	border:1px solid var(--dg-border); border-radius:8px; background:var(--dg-card); color:var(--dg-text); font-size:13px;",
    "}",
    "#cbi-diagnostics .diag-action { display:flex; align-items:center; }",
    "#cbi-diagnostics .diag-action .cbi-button { min-width:120px; padding:7px 14px; border-radius:8px; font-size:13px; font-weight:600; }",
    "#cbi-diagnostics .cbi-section {",
    "	background:var(--dg-card); border:1px solid var(--dg-border); border-radius:12px;",
    "	box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px;",
    "}",
    "#cbi-diagnostics #command-output textarea {",
    "	width:100% !important; box-sizing:border-box; padding:14px 16px;",
    "	border:1px solid var(--dg-border); border-radius:10px;",
    "	background:var(--dg-soft); color:var(--dg-text);",
    "	font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace !important; font-size:12px; line-height:1.6;",
    "}",
]
css_js = " +\n".join("\t\t\t" + repr(line + "\n") for line in css_lines)

new = (
    "\t\tview.setAttribute('id', 'cbi-diagnostics');\n"
    "\t\tvar css = '' +\n"
    + css_js
    + ";\n"
    "\t\tview.insertBefore(E('style', { 'data-ui-skin': 'diagnostics' }, [ css ]), view.firstChild);\n\n"
    "\t\treturn view;\n\t},"
)

t2 = t.replace(old, new, 1)
for must in (
    "#cbi-diagnostics",
    "data-ui-skin",
    "previousSibling.value",
    "handlePing",
    "handleTraceroute",
    "handleNslookup",
    "widget.command-output",
):
    if must not in t2:
        raise SystemExit(f"diagnostics.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    diagnostics.js skinned ({p})")
