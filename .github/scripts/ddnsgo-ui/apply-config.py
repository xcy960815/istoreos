#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if 'data-ui-skin="ddnsgo-config"' in t and "ddnsgo-pill" in t:
    print("SKIP  ddns-go config.js: already skinned")
    raise SystemExit(0)

old_render = """function renderStatus(isRunning, listen_port, noweb) {
    var statusText = isRunning ? _('RUNNING') : _('NOT RUNNING');
    var color = isRunning ? 'green' : 'red';
    var icon = isRunning ? '✓' : '✗';
    var html = String.format(
        '<em><span style="color:%s">%s <strong>%s %s</strong></span></em>',
        color, icon, _('DDNS-Go'), statusText
    );
    
    if (isRunning && res.pid) {
        html += ' <small>(PID: ' + res.pid + ')</small>';
    }
    
    if (isRunning && noweb !== '1') {
        const baseUrl = `${window.location.protocol}//${window.location.hostname}`;
        const fullUrl = `${baseUrl}:${listen_port}`;
        html += String.format('&#160;<a class="btn cbi-button" href="%s" target="_blank">%s</a>', fullUrl, _('Open Web Interface'));
     }
    
    return html;
}"""

new_render = """function renderStatus(isRunning, listen_port, noweb, pid) {
    var statusText = isRunning ? _('RUNNING') : _('NOT RUNNING');
    var pillClass = isRunning ? 'ddnsgo-pill ddnsgo-pill-ok' : 'ddnsgo-pill ddnsgo-pill-off';
    var html = '<span class="' + pillClass + '"><span class="ddnsgo-dot"></span>' +
        '%s %s'.format(_('DDNS-Go'), statusText) + '</span>';
    
    if (isRunning && pid) {
        html += ' <small class="ddnsgo-pid">(PID: ' + pid + ')</small>';
    }
    
    if (isRunning && noweb !== '1') {
        const baseUrl = `${window.location.protocol}//${window.location.hostname}`;
        const fullUrl = `${baseUrl}:${listen_port}`;
        html += String.format('&#160;<a class="btn cbi-button ddnsgo-linkbtn" href="%s" target="_blank">%s</a>', fullUrl, _('Open Web Interface'));
     }
    
    return html;
}"""

if old_render not in t:
    raise SystemExit("ddns-go config.js: renderStatus anchor not found")
t = t.replace(old_render, new_render, 1)

old_call = "statusView.innerHTML = renderStatus(res.running, listen_port, noweb);"
new_call = "statusView.innerHTML = renderStatus(res.running, listen_port, noweb, res.pid);"
if old_call not in t:
    raise SystemExit("ddns-go config.js: renderStatus() call anchor not found")
t = t.replace(old_call, new_call, 1)

old_bar = """            return E('div', { class: 'cbi-section', id: 'status_bar' }, [
                statusView,
                E('div', { 'style': 'text-align: right; font-style: italic;' }, [
                    E('span', {}, [
                        _('© github '),
                        E('a', { 
                            'href': 'https://github.com/sirpdboy', 
                            'target': '_blank',
                            'style': 'text-decoration: none;'
                        }, 'by sirpdboy')
                    ])
                ])
            ]);"""

if old_bar not in t:
    raise SystemExit("ddns-go config.js: status_bar anchor not found")

new_bar = """            return E('div', { class: 'cbi-section', id: 'status_bar' }, [
                E('div', { class: 'ddnsgo-card ddnsgo-status-card' }, [
                    E('div', { class: 'ddnsgo-row' }, [
                        E('span', { class: 'ddnsgo-label' }, _('Service status')),
                        statusView
                    ])
                ]),
                E('div', { 'class': 'ddnsgo-note', 'style': 'text-align: right; font-style: italic;' }, [
                    E('span', {}, [
                        _('© github '),
                        E('a', { 
                            'href': 'https://github.com/sirpdboy', 
                            'target': '_blank',
                            'style': 'text-decoration: none;'
                        }, 'by sirpdboy')
                    ])
                ])
            ]);"""

t = t.replace(old_bar, new_bar, 1)

old_ret = "\t\treturn m.render();\n\t}"
if old_ret not in t:
    raise SystemExit("ddns-go config.js: return m.render() anchor not found")

css_lines = [
    "#cbi-ddns-go {",
    "	--dg-accent: #5e72e4; --dg-ok: #2dce89; --dg-warn: #fb6340; --dg-border: #e9ecef;",
    "	--dg-muted: #8898aa; --dg-text: #32325d; --dg-card: #fff; --dg-soft: #f7f9fc;",
    "}",
    "#cbi-ddns-go.cbi-section, #cbi-ddns-go .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0 0 16px; }",
    'body[theme="dark"] #cbi-ddns-go { --dg-border:#3a3a3d; --dg-muted:#9aa2ad; --dg-text:#d7dae0; --dg-card:#232324; --dg-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-ddns-go { --dg-border:#3a3a3d; --dg-muted:#9aa2ad; --dg-text:#d7dae0; --dg-card:#232324; --dg-soft:#2b2b2d; } }',
    "#cbi-ddns-go > h2 { margin:0 0 6px; font-size:18px; font-weight:600; line-height:1.3; color:var(--dg-text); }",
    "#cbi-ddns-go .cbi-map-descr { margin:0 0 16px; font-size:13px; line-height:1.6; color:var(--dg-muted); }",
    "#cbi-ddns-go .ddnsgo-card, #cbi-ddns-go .cbi-section-node { background:var(--dg-card); border:1px solid var(--dg-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; }",
    "#cbi-ddns-go .ddnsgo-status-card { padding:16px 18px; }",
    "#cbi-ddns-go .ddnsgo-row { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }",
    "#cbi-ddns-go .ddnsgo-label { font-size:13px; color:var(--dg-muted); }",
    "#cbi-ddns-go .ddnsgo-pill { display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px; background:var(--dg-soft); font-size:13px; font-weight:600; color:var(--dg-text); }",
    "#cbi-ddns-go .ddnsgo-dot { width:10px; height:10px; border-radius:50%; background:var(--dg-muted); box-shadow:0 0 0 4px rgba(136,152,170,.12); }",
    "#cbi-ddns-go .ddnsgo-pill-ok .ddnsgo-dot { background:var(--dg-ok); box-shadow:0 0 0 4px rgba(45,206,137,.12); }",
    "#cbi-ddns-go .ddnsgo-pill-off .ddnsgo-dot { background:var(--dg-warn); box-shadow:0 0 0 4px rgba(251,99,64,.12); }",
    "#cbi-ddns-go .ddnsgo-pid { margin-left:8px; padding:4px 8px; border-radius:6px; background:var(--dg-soft); font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; color:var(--dg-muted); }",
    "#cbi-ddns-go .ddnsgo-linkbtn { display:inline-flex; align-items:center; margin-left:12px; padding:8px 14px; border-radius:8px; background:var(--dg-accent); color:#fff; font-size:13px; font-weight:600; text-decoration:none; }",
    "#cbi-ddns-go .ddnsgo-linkbtn:hover { filter:brightness(1.05); }",
    "#cbi-ddns-go #control_status { margin:0; min-height:1.5em; display:inline-flex; align-items:center; flex-wrap:wrap; gap:4px; font-size:13px; color:var(--dg-muted); }",
    "#cbi-ddns-go .ddnsgo-note { margin-top:8px; font-size:12px; color:var(--dg-muted); }",
    "#cbi-ddns-go .ddnsgo-note a { color:var(--dg-muted); }",
    "#cbi-ddns-go .cbi-value { padding:10px 0; border-bottom:1px solid var(--dg-border); }",
    "#cbi-ddns-go .cbi-value:last-child { border-bottom:0; padding-bottom:2px; }",
    "#cbi-ddns-go .cbi-value:first-child { padding-top:2px; }",
    "#cbi-ddns-go .cbi-value-title { color:var(--dg-text); font-size:13px; font-weight:600; }",
    "#cbi-ddns-go .cbi-value-description { color:var(--dg-muted); font-size:12px; line-height:1.6; }",
    "#cbi-ddns-go .cbi-page-actions { margin-top:16px; padding:0; border:0; background:none; }",
    "#cbi-ddns-go .cbi-page-actions .cbi-button { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; }",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)
new_ret = (
    "\t\treturn m.render().then(function(node) {\n"
    "\t\t\tnode.setAttribute('id', 'cbi-ddns-go');\n"
    "\t\t\tif (!node.querySelector('style[data-ui-skin=\"ddnsgo-config\"]')) {\n"
    "\t\t\t\tvar css = '' +\n"
    + css_js
    + ";\n"
    "\t\t\t\tnode.insertBefore(E('style', { 'data-ui-skin': 'ddnsgo-config' }, [ css ]), node.firstChild);\n"
    "\t\t\t}\n"
    "\t\t\treturn node;\n"
    "\t\t});\n"
    "\t}"
)
t = t.replace(old_ret, new_ret, 1)

po_path = None
for depth in range(3, 8):
    if depth >= len(p.parents):
        break
    cand = p.parents[depth] / "po" / "zh_Hans" / "ddns-go.po"
    if cand.is_file():
        po_path = cand
        break
if po_path:
    po = po_path.read_text(encoding="utf-8")
    if 'msgid "Service status"' not in po:
        po += '\nmsgid "Service status"\nmsgstr "服务状态"\n'
        po_path.write_text(po, encoding="utf-8")
        print("OK    ddns-go.po added: Service status")
    else:
        print("SKIP  ddns-go.po Service status present")
else:
    print("WARN  ddns-go.po not found")

for must in (
    "#cbi-ddns-go",
    'data-ui-skin="ddnsgo-config"',
    "ddnsgo-pill",
    "control_status",
    "status_bar",
    "checkProcess",
    "renderStatus(res.running, listen_port, noweb, res.pid)",
    "Open Web Interface",
    "skipverify",
):
    if must not in t:
        raise SystemExit(f"ddns-go config.js missing {must}")
p.write_text(t, encoding="utf-8")
print(f"OK    ddns-go config.js skinned ({p})")
