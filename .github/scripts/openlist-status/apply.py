#!/usr/bin/env python3
from pathlib import Path
import re
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "openlist-pill" in t:
    print("SKIP  openlist config.js: already skinned")
    raise SystemExit(0)

old_render = """function renderStatus(isRunning, port) {
	var spanTemp = '<span style="color:%s"><strong>%s %s</strong></span>';
	var renderHTML;
	if (isRunning) {
		var button = String.format('&#160;<a class="btn cbi-button" href="http://%s:%s" target="_blank" rel="noreferrer noopener">%s</a>',
			window.location.hostname, port, _('Open Web Interface'));
		renderHTML = spanTemp.format('green', _('OpenList'), _('RUNNING')) + button;
	} else {
		renderHTML = spanTemp.format('red', _('OpenList'), _('NOT RUNNING'));
	}

	return renderHTML;
}"""

new_render = """function renderStatus(isRunning, port) {
	var renderHTML;
	if (isRunning) {
		var button = String.format('<a class="openlist-linkbtn" href="http://%s:%s" target="_blank" rel="noreferrer noopener">%s</a>',
			window.location.hostname, port, _('Open Web Interface'));
		renderHTML = '<span class="openlist-pill openlist-pill-ok"><span class="openlist-dot"></span>' +
			'%s %s'.format(_('OpenList'), _('RUNNING')) + '</span>' + button;
	} else {
		renderHTML = '<span class="openlist-pill openlist-pill-off"><span class="openlist-dot"></span>' +
			'%s %s'.format(_('OpenList'), _('NOT RUNNING')) + '</span>';
	}
	return renderHTML;
}"""

if old_render not in t:
    raise SystemExit("openlist config.js: renderStatus anchor not found")
t = t.replace(old_render, new_render, 1)

pat = re.compile(
    r"return E\('div', \{ class: 'cbi-section', id: 'status_bar' \}, \[\s*"
    r"E\('p', \{ id: 'service_status' \}, _\('Collecting data\.\.\.'\)\)\s*"
    r"\]\);",
    re.M,
)
m = pat.search(t)
if not m:
    raise SystemExit("openlist config.js: status_bar anchor not found")

css_lines = [
    "#cbi-openlist-status {",
    "	--ol-accent: #5e72e4; --ol-ok: #2dce89; --ol-warn: #fb6340; --ol-border: #e9ecef;",
    "	--ol-muted: #8898aa; --ol-text: #32325d; --ol-card: #fff; --ol-soft: #f7f9fc;",
    "}",
    "#cbi-openlist-status.cbi-section, #cbi-openlist-status .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0; }",
    'body[theme="dark"] #cbi-openlist-status { --ol-border:#3a3a3d; --ol-muted:#9aa2ad; --ol-text:#d7dae0; --ol-card:#232324; --ol-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-openlist-status { --ol-border:#3a3a3d; --ol-muted:#9aa2ad; --ol-text:#d7dae0; --ol-card:#232324; --ol-soft:#2b2b2d; } }',
    "#cbi-openlist-status .openlist-card { background:var(--ol-card); border:1px solid var(--ol-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:16px 18px; margin:0 0 16px; }",
    "#cbi-openlist-status .openlist-row { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }",
    "#cbi-openlist-status .openlist-label { font-size:13px; color:var(--ol-muted); }",
    "#cbi-openlist-status .openlist-pill { display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px; background:var(--ol-soft); font-size:13px; font-weight:600; color:var(--ol-text); }",
    "#cbi-openlist-status .openlist-dot { width:10px; height:10px; border-radius:50%; background:var(--ol-muted); box-shadow:0 0 0 4px rgba(136,152,170,.12); }",
    "#cbi-openlist-status .openlist-pill-ok .openlist-dot { background:var(--ol-ok); box-shadow:0 0 0 4px rgba(45,206,137,.12); }",
    "#cbi-openlist-status .openlist-pill-off .openlist-dot { background:var(--ol-warn); box-shadow:0 0 0 4px rgba(251,99,64,.12); }",
    "#cbi-openlist-status .openlist-linkbtn { display:inline-flex; align-items:center; margin-left:12px; padding:8px 14px; border-radius:8px; background:var(--ol-accent); color:#fff; font-size:13px; font-weight:600; text-decoration:none; }",
    "#cbi-openlist-status .openlist-linkbtn:hover { filter:brightness(1.05); }",
    "#cbi-openlist-status #service_status { margin:0; min-height:1.5em; display:inline-flex; align-items:center; flex-wrap:wrap; gap:4px; }",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)
new_bar = (
    "return E('div', { id: 'cbi-openlist-status' }, [\n"
    "\t\t\t\tE('style', { 'data-ui-skin': 'openlist' }, [ '' +\n"
    + css_js
    + " ]),\n"
    "\t\t\t\tE('div', { class: 'cbi-section', id: 'status_bar' }, [\n"
    "\t\t\t\t\tE('div', { class: 'openlist-card' }, [\n"
    "\t\t\t\t\t\tE('div', { class: 'openlist-row' }, [\n"
    "\t\t\t\t\t\t\tE('span', { class: 'openlist-label' }, _('Service status')),\n"
    "\t\t\t\t\t\t\tE('p', { id: 'service_status' }, _('Collecting data...'))\n"
    "\t\t\t\t\t\t])\n"
    "\t\t\t\t\t])\n"
    "\t\t\t\t])\n"
    "\t\t\t]);"
)
t = t[: m.start()] + new_bar + t[m.end() :]

po_path = None
for depth in range(3, 8):
    if depth >= len(p.parents):
        break
    cand = p.parents[depth] / "po" / "zh_Hans" / "openlist.po"
    if cand.is_file():
        po_path = cand
        break
if po_path:
    po = po_path.read_text(encoding="utf-8")
    if 'msgid "Service status"' not in po:
        po += '\nmsgid "Service status"\nmsgstr "服务状态"\n'
        po_path.write_text(po, encoding="utf-8")
        print("OK    po: add Service status")
    else:
        print("SKIP  po: Service status present")
else:
    print("WARN  openlist zh_Hans po not found; Service status may stay English")

for must in (
    "service_status",
    "status_bar",
    "instance1",
    "Open Web Interface",
    "callServiceList",
    "openlist-pill",
    "#cbi-openlist-status",
    "data-ui-skin",
):
    if must not in t:
        raise SystemExit(f"openlist config.js missing {must}")
p.write_text(t, encoding="utf-8")
print(f"OK    openlist config.js status skinned ({p})")
