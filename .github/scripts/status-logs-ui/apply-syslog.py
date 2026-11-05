#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "'data-ui-skin': 'syslog'" in t and "#cbi-syslog" in t:
    print("SKIP  syslog.js: already skinned")
    raise SystemExit(0)

old = """\t\treturn E([], [
\t\t\tE('h2', {}, [ _('System Log') ]),
\t\t\tE('div', { 'id': 'content_syslog' }, [
\t\t\t\tE('div', { 'style': 'margin-bottom:10px' }, [
\t\t\t\t\tE('label', { 'for': 'invertLogFacilitySearch', 'style': 'margin-right:5px' }, _('Not')),
\t\t\t\t\tfacilityInvert,
\t\t\t\t\tE('label', { 'for': 'logFacilitySelect', 'style': 'margin: 0 5px' }, _('facility:')),
\t\t\t\t\tfacilitySelect,
\t\t\t\t\tE('label', { 'for': 'invertLogseveritySearch', 'style': 'margin: 0 5px' }, _('Not')),
\t\t\t\t\tseverityInvert,
\t\t\t\t\tE('label', { 'for': 'logSeveritySelect', 'style': 'margin: 0 5px' }, _('severity:')),
\t\t\t\t\tseveritySelect,
\t\t\t\t]),
\t\t\t\tE('div', { 'style': 'margin-bottom:10px' }, [
\t\t\t\t\tE('label', { 'for': 'invertLogTextSearch', 'style': 'margin-right:5px' }, _('Not')),
\t\t\t\t\tfilterTextInvert,
\t\t\t\t\tE('label', { 'for': 'logTextFilter', 'style': 'margin: 0 5px' }, _('including:')),
\t\t\t\t\tfilterTextInput,
\t\t\t\t]),
\t\t\t\tE('div', {'style': 'padding-bottom: 20px'}, [scrollDownButton]),
\t\t\t\tE('textarea', {
\t\t\t\t\t'id': 'syslog',
\t\t\t\t\t'style': 'font-size:12px',
\t\t\t\t\t'readonly': 'readonly',
\t\t\t\t\t'wrap': 'off',
\t\t\t\t\t'rows': loglines.rows,
\t\t\t\t}, [ loglines.value ]),
\t\t\t\tE('div', {'style': 'padding-bottom: 20px'}, [scrollUpButton])
\t\t\t])
\t\t]);"""

if old not in t:
    raise SystemExit("syslog.js: return E([], ...) anchor not found")

css_lines = [
    "#cbi-syslog {",
    "	--syslog-accent: #5e72e4; --syslog-border: #e9ecef; --syslog-muted: #8898aa;",
    "	--syslog-text: #32325d; --syslog-card: #fff; --syslog-soft: #f7f9fc;",
    "}",
    "#cbi-syslog.cbi-section, #cbi-syslog .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0; }",
    'body[theme="dark"] #cbi-syslog { --syslog-border:#3a3a3d; --syslog-muted:#9aa2ad; --syslog-text:#d7dae0; --syslog-card:#232324; --syslog-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-syslog { --syslog-border:#3a3a3d; --syslog-muted:#9aa2ad; --syslog-text:#d7dae0; --syslog-card:#232324; --syslog-soft:#2b2b2d; } }',
    "#cbi-syslog .syslog-card { background:var(--syslog-card); border:1px solid var(--syslog-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px; }",
    "#cbi-syslog .syslog-title { margin:0 0 14px; font-size:18px; font-weight:600; line-height:1.3; color:var(--syslog-text); }",
    "#cbi-syslog .syslog-filters { display:flex; flex-direction:column; gap:10px; padding:12px 14px; margin:0 0 14px; border-radius:10px; background:var(--syslog-soft); border:1px solid var(--syslog-border); }",
    "#cbi-syslog .syslog-filter-row { display:flex; align-items:center; flex-wrap:wrap; gap:8px; margin:0 !important; font-size:13px; color:var(--syslog-text); }",
    "#cbi-syslog .syslog-filter-row label { margin:0 2px 0 0 !important; font-size:13px; color:var(--syslog-muted); }",
    "#cbi-syslog .syslog-filter-row .cbi-input-select, #cbi-syslog .syslog-filter-row .cbi-input-text { margin:0 8px 0 0 !important; }",
    "#cbi-syslog .syslog-filter-row .cbi-input-checkbox { accent-color:var(--syslog-accent); }",
    "#cbi-syslog .syslog-actions { margin:0 0 12px; padding:0 !important; }",
    "#cbi-syslog .syslog-actions-bottom { margin:12px 0 0; padding:0 !important; }",
    "#cbi-syslog .cbi-button { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; }",
    "#cbi-syslog #syslog { width:100%; box-sizing:border-box; padding:14px 16px; border:1px solid var(--syslog-border); border-radius:10px; background:var(--syslog-soft); color:var(--syslog-text); font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px !important; line-height:1.6; }",
]
css_js = " +\n".join("\t\t\t\t" + repr(line + "\n") for line in css_lines)

new = (
    "\t\tvar css = '' +\n"
    + css_js
    + ";\n\n"
    "\t\treturn E('div', { 'id': 'cbi-syslog', 'class': 'cbi-map' }, [\n"
    "\t\t\tE('style', { 'data-ui-skin': 'syslog' }, [ css ]),\n"
    "\t\t\tE('div', { 'class': 'cbi-section' }, [\n"
    "\t\t\t\tE('div', { 'class': 'syslog-card' }, [\n"
    "\t\t\t\t\tE('h2', { 'class': 'syslog-title' }, [ _('System Log') ]),\n"
    "\t\t\t\t\tE('div', { 'id': 'content_syslog' }, [\n"
    "\t\t\t\t\t\tE('div', { 'class': 'syslog-filters' }, [\n"
    "\t\t\t\t\t\t\tE('div', { 'class': 'syslog-filter-row' }, [\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'invertLogFacilitySearch' }, _('Not')),\n"
    "\t\t\t\t\t\t\t\tfacilityInvert,\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'logFacilitySelect' }, _('facility:')),\n"
    "\t\t\t\t\t\t\t\tfacilitySelect,\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'invertLogseveritySearch' }, _('Not')),\n"
    "\t\t\t\t\t\t\t\tseverityInvert,\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'logSeveritySelect' }, _('severity:')),\n"
    "\t\t\t\t\t\t\t\tseveritySelect,\n"
    "\t\t\t\t\t\t\t]),\n"
    "\t\t\t\t\t\t\tE('div', { 'class': 'syslog-filter-row' }, [\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'invertLogTextSearch' }, _('Not')),\n"
    "\t\t\t\t\t\t\t\tfilterTextInvert,\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'logTextFilter' }, _('including:')),\n"
    "\t\t\t\t\t\t\t\tfilterTextInput,\n"
    "\t\t\t\t\t\t\t]),\n"
    "\t\t\t\t\t\t]),\n"
    "\t\t\t\t\t\tE('div', { 'class': 'syslog-actions' }, [scrollDownButton]),\n"
    "\t\t\t\t\t\tE('textarea', {\n"
    "\t\t\t\t\t\t\t'id': 'syslog',\n"
    "\t\t\t\t\t\t\t'style': 'font-size:12px',\n"
    "\t\t\t\t\t\t\t'readonly': 'readonly',\n"
    "\t\t\t\t\t\t\t'wrap': 'off',\n"
    "\t\t\t\t\t\t\t'rows': loglines.rows,\n"
    "\t\t\t\t\t\t}, [ loglines.value ]),\n"
    "\t\t\t\t\t\tE('div', { 'class': 'syslog-actions syslog-actions-bottom' }, [scrollUpButton])\n"
    "\t\t\t\t\t])\n"
    "\t\t\t\t])\n"
    "\t\t\t])\n"
    "\t\t]);"
)
t2 = t.replace(old, new, 1)
for must in (
    "#cbi-syslog",
    "'data-ui-skin': 'syslog'",
    "content_syslog",
    "scrollDownButton",
    "scrollUpButton",
    "invertLogFacilitySearch",
    "logFacilitySelect",
    "invertLogseveritySearch",
    "logSeveritySelect",
    "invertLogTextSearch",
    "logTextFilter",
    "syslog",
):
    if must not in t2:
        raise SystemExit(f"syslog.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    syslog.js skinned ({p})")
