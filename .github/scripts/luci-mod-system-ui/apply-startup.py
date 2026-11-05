#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-startup" in t:
    print("SKIP  startup.js: already skinned")
    raise SystemExit(0)

old = """\t\tui.tabs.initTabGroup(view.lastElementChild.childNodes);

\t\treturn view;"""

if old not in t:
    raise SystemExit("startup.js: initTabGroup anchor not found")

css_lines = [
    "#cbi-startup {",
    "	--su-accent: #5e72e4; --su-ok: #2dce89; --su-warn: #fb6340; --su-border: #e9ecef;",
    "	--su-muted: #8898aa; --su-text: #32325d; --su-card: #fff; --su-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-startup { --su-border:#3a3a3d; --su-muted:#9aa2ad; --su-text:#d7dae0; --su-card:#232324; --su-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-startup { --su-border:#3a3a3d; --su-muted:#9aa2ad; --su-text:#d7dae0; --su-card:#232324; --su-soft:#2b2b2d; } }',
    "#cbi-startup > h2 { margin:0 0 12px; font-size:18px; font-weight:600; line-height:1.3; color:var(--su-text); }",
    "#cbi-startup .cbi-tabmenu { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 16px; padding:6px; border:1px solid var(--su-border); border-radius:10px; background:var(--su-soft); list-style:none; }",
    "#cbi-startup .cbi-tabmenu > li { margin:0; border:0; background:none; }",
    "#cbi-startup .cbi-tabmenu > li > a { display:inline-block; padding:6px 16px; border-radius:8px; font-size:13px; font-weight:600; color:var(--su-muted); text-decoration:none; }",
    "#cbi-startup .cbi-tabmenu > li.cbi-tab > a { background:var(--su-accent); color:#fff; }",
    "#cbi-startup [data-tab=\"init\"], #cbi-startup [data-tab=\"rc\"] {",
    "	background:var(--su-card); border:1px solid var(--su-border); border-radius:12px;",
    "	box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px;",
    "}",
    "#cbi-startup [data-tab] > p:first-child { margin:0 0 14px; font-size:13px; line-height:1.6; color:var(--su-muted); }",
    "#cbi-startup [data-tab] > p:first-child strong { color:var(--su-warn); font-weight:600; }",
    "#cbi-startup table.table { width:100%; border-collapse:separate; border-spacing:0; border:1px solid var(--su-border); border-radius:10px; overflow:hidden; }",
    "#cbi-startup .table .tr.table-titles .th { background:var(--su-soft); color:var(--su-muted); font-size:12px; font-weight:600; padding:10px 14px; border-bottom:1px solid var(--su-border); text-align:left; }",
    "#cbi-startup .table .tr:not(.table-titles) .td { padding:10px 14px; font-size:13px; color:var(--su-text); border-bottom:1px solid var(--su-border); vertical-align:middle; }",
    "#cbi-startup .table .tr:last-child .td { border-bottom:0; }",
    "#cbi-startup .table .td > div { display:flex; flex-wrap:wrap; gap:6px; align-items:center; justify-content:flex-end; }",
    "#cbi-startup .table .btn { padding:5px 12px; border-radius:8px; font-size:12px; font-weight:600; min-width:68px; }",
    "#cbi-startup .table .cbi-button-positive { background:rgba(45,206,137,.14) !important; border-color:rgba(45,206,137,.35) !important; color:var(--su-ok) !important; }",
    "#cbi-startup .table .cbi-button-negative { background:rgba(251,99,64,.14) !important; border-color:rgba(251,99,64,.35) !important; color:var(--su-warn) !important; }",
    "#cbi-startup [data-tab=\"rc\"] textarea {",
    "	width:100% !important; box-sizing:border-box; padding:14px 16px;",
    "	border:1px solid var(--su-border); border-radius:10px;",
    "	background:var(--su-soft); color:var(--su-text);",
    "	font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; line-height:1.6;",
    "}",
    "#cbi-startup .cbi-page-actions { display:flex; justify-content:flex-end; gap:10px; margin:14px 0 0; padding:14px 0 0; border-top:1px solid var(--su-border); background:none; }",
    "#cbi-startup .cbi-page-actions .btn { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; font-weight:600; }",
]
css_js = " +\n".join("\t\t\t" + repr(line + "\n") for line in css_lines)

new = (
    "\t\tui.tabs.initTabGroup(view.lastElementChild.childNodes);\n\n"
    "\t\tview.setAttribute('id', 'cbi-startup');\n"
    "\t\tview.classList.add('cbi-map');\n"
    "\t\tvar css = '' +\n"
    + css_js
    + ";\n"
    "\t\tview.insertBefore(E('style', { 'data-ui-skin': 'startup' }, [ css ]), view.firstChild);\n\n"
    "\t\treturn view;"
)

t2 = t.replace(old, new, 1)
for must in ("#cbi-startup", "data-ui-skin", "callRcList", "callRcInit", "/etc/rc.local", "handleRcLocalSave"):
    if must not in t2:
        raise SystemExit(f"startup.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    startup.js skinned ({p})")
