#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "'data-ui-skin': 'ttyd'" in t and "#cbi-ttyd" in t:
    print("SKIP  term.js: already skinned")
    raise SystemExit(0)

for must in ("uci.load('ttyd')", "url_override", "port=0"):
    if must not in t:
        raise SystemExit(f"term.js precheck missing {must}")

old = """\t\treturn E('iframe', {
\t\t\tsrc: url || ((ssl === '1' ? 'https' : 'http') + '://' + window.location.hostname + ':' + port),
\t\t\tstyle: 'width: 100%; min-height: 500px; border: none; border-radius: 3px; resize: vertical;'
\t\t});"""

if old not in t:
    raise SystemExit("term.js: return E('iframe', ...) anchor not found")

css_lines = [
    "#cbi-ttyd {",
    "	--ttyd-accent: #5e72e4; --ttyd-border: #e9ecef; --ttyd-muted: #8898aa;",
    "	--ttyd-text: #32325d; --ttyd-card: #fff; --ttyd-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-ttyd { --ttyd-border:#3a3a3d; --ttyd-muted:#9aa2ad; --ttyd-text:#d7dae0; --ttyd-card:#232324; --ttyd-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-ttyd { --ttyd-border:#3a3a3d; --ttyd-muted:#9aa2ad; --ttyd-text:#d7dae0; --ttyd-card:#232324; --ttyd-soft:#2b2b2d; } }',
    "#cbi-ttyd.cbi-map, #cbi-ttyd .cbi-map { padding: 0; margin: 0; }",
    "#cbi-ttyd .ttyd-head {",
    "	display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px 16px;",
    "	padding: 16px 22px; margin: 0 0 16px; background: var(--ttyd-card); border: 1px solid var(--ttyd-border);",
    "	border-radius: 12px; box-shadow: 0 2px 12px rgba(50,50,93,.06);",
    "}",
    "#cbi-ttyd .ttyd-title { margin: 0 0 4px; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--ttyd-text); }",
    "#cbi-ttyd .ttyd-head .cbi-map-descr { margin: 0; font-size: 13px; line-height: 1.6; color: var(--ttyd-muted); }",
    "#cbi-ttyd .ttyd-port-badge {",
    "	display: inline-block; padding: 2px 8px; border-radius: 4px; background: var(--ttyd-soft);",
    "	border: 1px solid var(--ttyd-border); font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;",
    "	font-size: 12px; color: var(--ttyd-text); font-weight: 600; margin-left: 4px;",
    "}",
    "#cbi-ttyd .ttyd-open-btn {",
    "	display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 8px; font-size: 13px;",
    "	font-weight: 600; background: var(--ttyd-accent); color: #fff !important; text-decoration: none;",
    "	box-shadow: 0 2px 6px rgba(94, 114, 228, .25); transition: all .15s ease;",
    "}",
    "#cbi-ttyd .ttyd-open-btn:hover { filter: brightness(1.08); text-decoration: none; }",
    "#cbi-ttyd .ttyd-window {",
    "	background: #1e1e24; border: 1px solid var(--ttyd-border); border-radius: 12px;",
    "	box-shadow: 0 4px 20px rgba(0,0,0,.15); overflow: hidden; margin: 0 0 16px;",
    "}",
    "#cbi-ttyd .ttyd-window-bar {",
    "	display: flex; align-items: center; padding: 10px 14px; background: #2b2b36;",
    "	border-bottom: 1px solid rgba(255,255,255,.08); position: relative;",
    "}",
    "#cbi-ttyd .ttyd-dots { display: flex; align-items: center; gap: 6px; z-index: 1; }",
    "#cbi-ttyd .ttyd-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }",
    "#cbi-ttyd .ttyd-dot-red { background: #ff5f56; }",
    "#cbi-ttyd .ttyd-dot-yellow { background: #ffbd2e; }",
    "#cbi-ttyd .ttyd-dot-green { background: #27c93f; }",
    "#cbi-ttyd .ttyd-window-title {",
    "	position: absolute; left: 0; right: 0; text-align: center;",
    "	font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px;",
    "	color: rgba(255,255,255,.6); pointer-events: none;",
    "}",
    "#cbi-ttyd .ttyd-iframe {",
    "	width: 100%; height: calc(100vh - 240px); min-height: 540px; border: none; display: block;",
    "	background: #000; resize: vertical;",
    "}",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)

new = """\t\tvar targetUrl = url || ((ssl === '1' ? 'https' : 'http') + '://' + window.location.hostname + ':' + port);
\t\tvar css = '' +
""" + css_js + """;

\t\treturn E('div', { 'id': 'cbi-ttyd', 'class': 'cbi-map' }, [
\t\t\tE('style', { 'data-ui-skin': 'ttyd' }, [ css ]),
\t\t\tE('div', { 'class': 'ttyd-head' }, [
\t\t\t\tE('div', { 'class': 'ttyd-head-left' }, [
\t\t\t\t\tE('h2', { 'class': 'ttyd-title' }, _('Terminal')),
\t\t\t\t\tE('div', { 'class': 'cbi-map-descr' }, [
\t\t\t\t\t\t_('Web-based terminal access to the system command line.') + ' ',
\t\t\t\t\t\tE('span', { 'class': 'ttyd-port-badge' }, [ _('Port') + ': ' + port ])
\t\t\t\t\t])
\t\t\t\t]),
\t\t\t\tE('div', { 'class': 'ttyd-head-right' }, [
\t\t\t\t\tE('a', {
\t\t\t\t\t\t'class': 'ttyd-open-btn',
\t\t\t\t\t\t'href': targetUrl,
\t\t\t\t\t\t'target': '_blank',
\t\t\t\t\t\t'rel': 'noopener noreferrer'
\t\t\t\t\t}, [
\t\t\t\t\t\t_('Open in new tab'),
\t\t\t\t\t\tE('span', { 'class': 'ttyd-external-icon' }, ' ↗')
\t\t\t\t\t])
\t\t\t\t])
\t\t\t]),
\t\t\tE('div', { 'class': 'ttyd-window' }, [
\t\t\t\tE('div', { 'class': 'ttyd-window-bar' }, [
\t\t\t\t\tE('div', { 'class': 'ttyd-dots' }, [
\t\t\t\t\t\tE('span', { 'class': 'ttyd-dot ttyd-dot-red' }),
\t\t\t\t\t\tE('span', { 'class': 'ttyd-dot ttyd-dot-yellow' }),
\t\t\t\t\t\tE('span', { 'class': 'ttyd-dot ttyd-dot-green' })
\t\t\t\t\t]),
\t\t\t\t\tE('div', { 'class': 'ttyd-window-title' }, 'root@iStoreOS ~ ttyd')
\t\t\t\t]),
\t\t\t\tE('iframe', {
\t\t\t\t\t'src': targetUrl,
\t\t\t\t\t'class': 'ttyd-iframe'
\t\t\t\t})
\t\t\t])
\t\t]);"""

t2 = t.replace(old, new, 1)
if t2 == t:
    raise SystemExit("term.js replace failed")

for must in ("uci.load('ttyd')", "data-ui-skin", "#cbi-ttyd", "ttyd-head", "ttyd-window"):
    if must not in t2:
        raise SystemExit(f"term.js missing {must}")

p.write_text(t2, encoding="utf-8")
print(f"OK    term.js skinned ({p})")

# 顺便追加 po 翻译
app_dir = p.parents[5]  # applications/luci-app-ttyd
po_entries = [
    ('Open in new tab', '在新标签页打开'),
    ('Web-based terminal access to the system command line.', '通过 Web 终端访问系统命令行。'),
]
for po_name in ('zh_Hans', 'zh-cn'):
    po_file = app_dir / 'po' / po_name / 'ttyd.po'
    if po_file.exists():
        po_content = po_file.read_text(encoding='utf-8')
        appended = False
        for msgid, msgstr in po_entries:
            if f'msgid "{msgid}"' not in po_content:
                po_content += f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'
                appended = True
        if appended:
            po_file.write_text(po_content, encoding='utf-8')
            print(f"OK    appended translations to {po_file}")
