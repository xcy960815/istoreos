#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "'data-ui-skin': 'dmesg'" in t and "#cbi-dmesg" in t:
    print("SKIP  dmesg.js: already skinned")
    raise SystemExit(0)

old = """\t\treturn E([], [
\t\t\tE('h2', {}, [ _('Kernel Log') ]),
\t\t\tE('div', { 'id': 'content_syslog' }, [
\t\t\t\tE('div', { 'style': 'margin-bottom:10px' }, [
\t\t\t\t\tE('label', { 'for': 'invertLogFacilitySearch', 'style': 'margin-right:5px' }, _('Not')),
\t\t\t\t\trangeTimeInvert,
\t\t\t\t\tE('label', { 'for': 'logFacilitySelect', 'style': 'margin: 0 5px' }, _('between:')),
\t\t\t\t\tfromTimeFilter,
\t\t\t\t\tE('label', { 'for': 'logSeveritySelect', 'style': 'margin: 0 5px' }, _('and:')),
\t\t\t\t\ttoTimeFilter,
\t\t\t\t]),
\t\t\t\tE('div', { 'style': 'margin-bottom:10px' }, [
\t\t\t\t\tE('label', { 'for': 'invertLogSeveritySearch', 'style': 'margin-right:5px' }, _('Not')),
\t\t\t\t\tseverityInvert,
\t\t\t\t\t'\\xa0',
\t\t\t\t\tseveritySelect,
\t\t\t\t\tE('label', { 'for': 'logSeveritySelect', 'style': 'margin: 0 5px' }, _('and above')),
\t\t\t\t]),
\t\t\t\tE('div', { 'style': 'margin-bottom:10px' }, [
\t\t\t\t\tE('label', { 'for': 'invertAscendingSort', 'style': 'margin-right:5px' }, _('Reverse sort')),
\t\t\t\t\tdescendingSort,
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
\t\t\t\t\t'rows': loglines.rows
\t\t\t\t}, [ loglines.value ]),
\t\t\t\tE('div', {'style': 'padding-bottom: 20px'}, [scrollUpButton])
\t\t\t])
\t\t]);"""

if old not in t:
    raise SystemExit("dmesg.js: return E([], ...) anchor not found")

css_lines = [
    "#cbi-dmesg {",
    "	--dmesg-accent: #5e72e4; --dmesg-border: #e9ecef; --dmesg-muted: #8898aa;",
    "	--dmesg-text: #32325d; --dmesg-card: #fff; --dmesg-soft: #f7f9fc;",
    "}",
    "#cbi-dmesg.cbi-section, #cbi-dmesg .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0; }",
    'body[theme="dark"] #cbi-dmesg { --dmesg-border:#3a3a3d; --dmesg-muted:#9aa2ad; --dmesg-text:#d7dae0; --dmesg-card:#232324; --dmesg-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-dmesg { --dmesg-border:#3a3a3d; --dmesg-muted:#9aa2ad; --dmesg-text:#d7dae0; --dmesg-card:#232324; --dmesg-soft:#2b2b2d; } }',
    "#cbi-dmesg .dmesg-card { background:var(--dmesg-card); border:1px solid var(--dmesg-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px; }",
    "#cbi-dmesg .dmesg-title { margin:0 0 14px; font-size:18px; font-weight:600; line-height:1.3; color:var(--dmesg-text); }",
    "#cbi-dmesg .dmesg-filters { display:flex; flex-direction:column; gap:10px; padding:12px 14px; margin:0 0 14px; border-radius:10px; background:var(--dmesg-soft); border:1px solid var(--dmesg-border); }",
    "#cbi-dmesg .dmesg-filter-row { display:flex; align-items:center; flex-wrap:wrap; gap:8px; margin:0 !important; font-size:13px; color:var(--dmesg-text); }",
    "#cbi-dmesg .dmesg-filter-row label { margin:0 2px 0 0 !important; font-size:13px; color:var(--dmesg-muted); }",
    "#cbi-dmesg .dmesg-filter-row .cbi-input-select, #cbi-dmesg .dmesg-filter-row .cbi-input-text { margin:0 8px 0 0 !important; }",
    "#cbi-dmesg .dmesg-filter-row .cbi-input-checkbox { accent-color:var(--dmesg-accent); }",
    "#cbi-dmesg .dmesg-actions { margin:0 0 12px; padding:0 !important; }",
    "#cbi-dmesg .dmesg-actions-bottom { margin:12px 0 0; padding:0 !important; }",
    "#cbi-dmesg .cbi-button { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; }",
    "#cbi-dmesg #syslog { width:100%; box-sizing:border-box; padding:14px 16px; border:1px solid var(--dmesg-border); border-radius:10px; background:var(--dmesg-soft); color:var(--dmesg-text); font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px !important; line-height:1.6; }",
]
css_js = " +\n".join("\t\t\t\t" + repr(line + "\n") for line in css_lines)

new = (
    "\t\tvar css = '' +\n"
    + css_js
    + ";\n\n"
    "\t\treturn E('div', { 'id': 'cbi-dmesg', 'class': 'cbi-map' }, [\n"
    "\t\t\tE('style', { 'data-ui-skin': 'dmesg' }, [ css ]),\n"
    "\t\t\tE('div', { 'class': 'cbi-section' }, [\n"
    "\t\t\t\tE('div', { 'class': 'dmesg-card' }, [\n"
    "\t\t\t\t\tE('h2', { 'class': 'dmesg-title' }, [ _('Kernel Log') ]),\n"
    "\t\t\t\t\tE('div', { 'id': 'content_syslog' }, [\n"
    "\t\t\t\t\t\tE('div', { 'class': 'dmesg-filters' }, [\n"
    "\t\t\t\t\t\t\tE('div', { 'class': 'dmesg-filter-row' }, [\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'invertLogFacilitySearch' }, _('Not')),\n"
    "\t\t\t\t\t\t\t\trangeTimeInvert,\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'logFacilitySelect' }, _('between:')),\n"
    "\t\t\t\t\t\t\t\tfromTimeFilter,\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'logSeveritySelect' }, _('and:')),\n"
    "\t\t\t\t\t\t\t\ttoTimeFilter,\n"
    "\t\t\t\t\t\t\t]),\n"
    "\t\t\t\t\t\t\tE('div', { 'class': 'dmesg-filter-row' }, [\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'invertLogSeveritySearch' }, _('Not')),\n"
    "\t\t\t\t\t\t\t\tseverityInvert,\n"
    "\t\t\t\t\t\t\t\t'\\xa0',\n"
    "\t\t\t\t\t\t\t\tseveritySelect,\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'logSeveritySelect' }, _('and above')),\n"
    "\t\t\t\t\t\t\t]),\n"
    "\t\t\t\t\t\t\tE('div', { 'class': 'dmesg-filter-row' }, [\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'invertAscendingSort' }, _('Reverse sort')),\n"
    "\t\t\t\t\t\t\t\tdescendingSort,\n"
    "\t\t\t\t\t\t\t]),\n"
    "\t\t\t\t\t\t\tE('div', { 'class': 'dmesg-filter-row' }, [\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'invertLogTextSearch' }, _('Not')),\n"
    "\t\t\t\t\t\t\t\tfilterTextInvert,\n"
    "\t\t\t\t\t\t\t\tE('label', { 'for': 'logTextFilter' }, _('including:')),\n"
    "\t\t\t\t\t\t\t\tfilterTextInput,\n"
    "\t\t\t\t\t\t\t]),\n"
    "\t\t\t\t\t\t]),\n"
    "\t\t\t\t\t\tE('div', { 'class': 'dmesg-actions' }, [scrollDownButton]),\n"
    "\t\t\t\t\t\tE('textarea', {\n"
    "\t\t\t\t\t\t\t'id': 'syslog',\n"
    "\t\t\t\t\t\t\t'style': 'font-size:12px',\n"
    "\t\t\t\t\t\t\t'readonly': 'readonly',\n"
    "\t\t\t\t\t\t\t'wrap': 'off',\n"
    "\t\t\t\t\t\t\t'rows': loglines.rows\n"
    "\t\t\t\t\t\t}, [ loglines.value ]),\n"
    "\t\t\t\t\t\tE('div', { 'class': 'dmesg-actions dmesg-actions-bottom' }, [scrollUpButton])\n"
    "\t\t\t\t\t])\n"
    "\t\t\t\t])\n"
    "\t\t\t])\n"
    "\t\t]);"
)
t2 = t.replace(old, new, 1)
for must in (
    "#cbi-dmesg",
    "'data-ui-skin': 'dmesg'",
    "content_syslog",
    "scrollDownButton",
    "scrollUpButton",
    "invertLogRangeTime",
    "logFromTime",
    "logToTime",
    "invertSeverity",
    "logSeveritySelect",
    "invertAscendingSort",
    "invertLogTextSearch",
    "logTextFilter",
    "syslog",
):
    if must not in t2:
        raise SystemExit(f"dmesg.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    dmesg.js skinned ({p})")
