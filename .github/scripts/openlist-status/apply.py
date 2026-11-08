#!/usr/bin/env python3
from pathlib import Path
import re
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "openlist-pill" in t and "#cbi-openlist" in t:
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

if old_render in t:
    t = t.replace(old_render, new_render, 1)
elif "openlist-pill" not in t:
    raise SystemExit("openlist config.js: renderStatus anchor not found")

pat = re.compile(
    r"return E\('div', \{ class: 'cbi-section', id: 'status_bar' \}, \[\s*"
    r"E\('p', \{ id: 'service_status' \}, _\('Collecting data\.\.\.'\)\)\s*"
    r"\]\);",
    re.M,
)
m = pat.search(t)
if m:
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
elif "#cbi-openlist-status" not in t:
    raise SystemExit("openlist config.js: status_bar anchor not found")

old_tail = "\t\treturn m.render();\n\t}"
if old_tail in t:
    form_css_lines = [
        "#cbi-openlist {",
        "	--ol-accent: #5e72e4; --ol-ok: #2dce89; --ol-warn: #fb6340; --ol-border: #e9ecef;",
        "	--ol-muted: #8898aa; --ol-text: #32325d; --ol-card: #fff; --ol-soft: #f7f9fc;",
        "}",
        'body[theme="dark"] #cbi-openlist { --ol-border:#3a3a3d; --ol-muted:#9aa2ad; --ol-text:#d7dae0; --ol-card:#232324; --ol-soft:#2b2b2d; }',
        '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-openlist { --ol-border:#3a3a3d; --ol-muted:#9aa2ad; --ol-text:#d7dae0; --ol-card:#232324; --ol-soft:#2b2b2d; } }',
        "#cbi-openlist > h2 { margin:0 0 6px; font-size:18px; font-weight:600; line-height:1.3; color:var(--ol-text); }",
        "#cbi-openlist .cbi-map-descr { margin:0 0 16px; font-size:13px; line-height:1.6; color:var(--ol-muted); }",
        "#cbi-openlist .cbi-map-descr code, #cbi-openlist .openlist-head > .cbi-map-descr code { padding:2px 6px; border-radius:6px; background:var(--ol-soft); color:var(--ol-text); font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; }",
        "#cbi-openlist .openlist-head { display:flex; align-items:baseline; justify-content:space-between; gap:8px 16px; flex-wrap:wrap; margin:0 0 16px; padding:16px 22px; background:var(--ol-card); border:1px solid var(--ol-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); }",
        "#cbi-openlist .openlist-head > h2 { margin:0; font-size:18px; font-weight:600; line-height:1.3; color:var(--ol-text); }",
        "#cbi-openlist .openlist-head > .cbi-map-descr { margin:0 0 0 auto; font-size:13px; line-height:1.6; color:var(--ol-muted); text-align:right; }",
        "#cbi-openlist .cbi-section:not(#status_bar) { background:var(--ol-card); border:1px solid var(--ol-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px; }",
        "#cbi-openlist .cbi-section:not(#status_bar) > h3, #cbi-openlist .cbi-section-title { margin:0 0 12px; font-size:16px; font-weight:600; line-height:1.3; color:var(--ol-text); }",
        "#cbi-openlist .cbi-value { display:flex; align-items:flex-start; gap:16px; padding:12px 0; margin:0; border-top:1px solid var(--ol-border); border-bottom:0; flex-wrap:wrap; }",
        "#cbi-openlist .cbi-value:first-child { border-top:0; padding-top:4px; }",
        "#cbi-openlist .cbi-value:last-child { padding-bottom:4px; }",
        "#cbi-openlist .cbi-value-title { width:190px; flex-shrink:0; padding:6px 0 0; font-size:13px; font-weight:600; color:var(--ol-text); text-align:left; }",
        "#cbi-openlist .cbi-value-field { flex:1; min-width:220px; text-align:left; }",
        "#cbi-openlist .cbi-value-description { margin:6px 0 0; font-size:12px; line-height:1.6; color:var(--ol-muted); }",
        "#cbi-openlist .cbi-page-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:4px; padding:0; border:0; background:none; }",
        "#cbi-openlist .cbi-page-actions .cbi-button { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; font-weight:600; }",
    ]
    form_css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in form_css_lines)
    new_tail = (
        "\t\treturn m.render().then(function(node) {\n"
        "\t\t\tnode.setAttribute('id', 'cbi-openlist');\n"
        "\t\t\tvar css = '' +\n"
        + form_css_js
        + ";\n"
        "\t\t\tvar skin = function() {\n"
        "\t\t\t\tvar h2 = null, descr = null, kids = node.children, i;\n"
        "\t\t\t\tfor (i = 0; i < kids.length; i++) {\n"
        "\t\t\t\t\tif (!h2 && kids[i].tagName === 'H2')\n"
        "\t\t\t\t\t\th2 = kids[i];\n"
        "\t\t\t\t\telse if (!descr && kids[i].classList && kids[i].classList.contains('cbi-map-descr'))\n"
        "\t\t\t\t\t\tdescr = kids[i];\n"
        "\t\t\t\t}\n"
        "\t\t\t\tif (h2 && descr && !node.querySelector('.openlist-head')) {\n"
        "\t\t\t\t\tvar head = document.createElement('div');\n"
        "\t\t\t\t\thead.className = 'openlist-head';\n"
        "\t\t\t\t\tnode.insertBefore(head, h2);\n"
        "\t\t\t\t\thead.appendChild(h2);\n"
        "\t\t\t\t\thead.appendChild(descr);\n"
        "\t\t\t\t}\n"
        "\t\t\t\tif (!node.querySelector('style[data-ui-skin=\"openlist-form\"]'))\n"
        "\t\t\t\t\tnode.insertBefore(E('style', { 'data-ui-skin': 'openlist-form' }, [ css ]), node.firstChild);\n"
        "\t\t\t};\n"
        "\t\t\tskin();\n"
        "\t\t\treturn node;\n"
        "\t\t});\n\t}"
    )
    t = t.replace(old_tail, new_tail, 1)
elif "#cbi-openlist" not in t:
    raise SystemExit("openlist config.js: return m.render() anchor not found")

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
    "#cbi-openlist",
    "openlist-head",
    "data-ui-skin",
):
    if must not in t:
        raise SystemExit(f"openlist config.js missing {must}")
p.write_text(t, encoding="utf-8")
print(f"OK    openlist config.js skinned ({p})")
