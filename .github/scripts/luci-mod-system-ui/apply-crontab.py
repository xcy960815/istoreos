#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-crontab" in t:
    print("SKIP  crontab.js: already skinned")
    raise SystemExit(0)

old = """\trender: function(crontab) {
\t\treturn E([
\t\t\tE('h2', _('Scheduled Tasks')),
\t\t\tE('p', { 'class': 'cbi-section-descr' }, _('This is the system crontab in which scheduled tasks can be defined.')),
\t\t\tE('p', {}, E('textarea', { 'style': 'width:100%', 'rows': 25, 'disabled': isReadonlyView }, [ crontab != null ? crontab : '' ]))
\t\t]);
\t},"""

if old not in t:
    raise SystemExit("crontab.js: render anchor not found")

css_lines = [
    "#cbi-crontab {",
    "	--cron-accent: #5e72e4; --cron-border: #e9ecef; --cron-muted: #8898aa;",
    "	--cron-text: #32325d; --cron-card: #fff; --cron-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-crontab { --cron-border:#3a3a3d; --cron-muted:#9aa2ad; --cron-text:#d7dae0; --cron-card:#232324; --cron-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-crontab { --cron-border:#3a3a3d; --cron-muted:#9aa2ad; --cron-text:#d7dae0; --cron-card:#232324; --cron-soft:#2b2b2d; } }',
    "#cbi-crontab > h2 { margin:0 0 12px; font-size:18px; font-weight:600; line-height:1.3; color:var(--cron-text); }",
    "#cbi-crontab .cbi-section {",
    "	background:var(--cron-card); border:1px solid var(--cron-border); border-radius:12px;",
    "	box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px;",
    "}",
    "#cbi-crontab .cbi-section-descr { margin:0 0 14px; font-size:13px; line-height:1.6; color:var(--cron-muted); }",
    "#cbi-crontab p { margin:0; }",
    "#cbi-crontab textarea {",
    "	width:100% !important; box-sizing:border-box; padding:14px 16px;",
    "	border:1px solid var(--cron-border); border-radius:10px;",
    "	background:var(--cron-soft); color:var(--cron-text);",
    "	font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; line-height:1.6;",
    "	resize:vertical;",
    "}",
]
css_js = " +\n".join("\t\t\t\t" + repr(line + "\n") for line in css_lines)

new = (
    "\trender: function(crontab) {\n"
    "\t\tvar css = '' +\n"
    + css_js
    + ";\n"
    "\t\treturn E('div', { 'id': 'cbi-crontab', 'class': 'cbi-map' }, [\n"
    "\t\t\tE('style', { 'data-ui-skin': 'crontab' }, [ css ]),\n"
    "\t\t\tE('h2', _('Scheduled Tasks')),\n"
    "\t\t\tE('div', { 'class': 'cbi-section' }, [\n"
    "\t\t\t\tE('p', { 'class': 'cbi-section-descr' }, _('This is the system crontab in which scheduled tasks can be defined.')),\n"
    "\t\t\t\tE('p', {}, E('textarea', { 'style': 'width:100%', 'rows': 25, 'disabled': isReadonlyView }, [ crontab != null ? crontab : '' ]))\n"
    "\t\t\t])\n"
    "\t\t]);\n"
    "\t},"
)

t2 = t.replace(old, new, 1)
for must in ("#cbi-crontab", "data-ui-skin", "/etc/crontabs/root", "/etc/init.d/cron", "handleSave"):
    if must not in t2:
        raise SystemExit(f"crontab.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    crontab.js skinned ({p})")
