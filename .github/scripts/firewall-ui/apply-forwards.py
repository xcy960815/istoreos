#!/usr/bin/env python3
"""
luci-app-firewall forwards.js (端口转发) 页面样式卡片化换皮
- 顶部白卡头 .forwards-head 统一标题与说明
- 规则表格卡片化、区域徽章圆角化、操作按钮与右下角保存栏
"""

from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-firewall-forwards" in t:
    print("SKIP  forwards.js: already skinned")
    raise SystemExit(0)

old_render = "\t\treturn m.render();\n\t}\n});"

css_lines = [
    "#cbi-firewall-forwards {",
    "	--fw-accent: #5e72e4; --fw-ok: #2dce89; --fw-warn: #fb6340; --fw-danger: #f5365c; --fw-border: #e9ecef;",
    "	--fw-muted: #8898aa; --fw-text: #32325d; --fw-card: #fff; --fw-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-firewall-forwards { --fw-border:#3a3a3d; --fw-muted:#9aa2ad; --fw-text:#d7dae0; --fw-card:#232324; --fw-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-firewall-forwards { --fw-border:#3a3a3d; --fw-muted:#9aa2ad; --fw-text:#d7dae0; --fw-card:#232324; --fw-soft:#2b2b2d; } }',
    "#cbi-firewall-forwards.cbi-map, #cbi-firewall-forwards .cbi-map { padding: 0; margin: 0; }",
    "#cbi-firewall-forwards .forwards-head {",
    "	display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px 20px;",
    "	padding: 18px 24px; margin: 0 0 16px; background: var(--fw-card); border: 1px solid var(--fw-border);",
    "	border-radius: 12px; box-shadow: 0 2px 12px rgba(50,50,93,.06);",
    "}",
    "#cbi-firewall-forwards .forwards-head-left h2 { margin: 0; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--fw-text); }",
    "#cbi-firewall-forwards .forwards-head-right .cbi-map-descr { margin: 0; font-size: 13px; line-height: 1.5; color: var(--fw-muted); max-width: 540px; text-align: right; }",
    "@media (max-width: 768px) { #cbi-firewall-forwards .forwards-head-right .cbi-map-descr { text-align: left; } }",
    "/* 端口转发网格卡片化 */",
    "#cbi-firewall-forwards .cbi-section {",
    "	background: var(--fw-card); border: 1px solid var(--fw-border); border-radius: 12px;",
    "	box-shadow: 0 2px 12px rgba(50,50,93,.06); padding: 20px 22px; margin: 0 0 16px; box-sizing: border-box;",
    "}",
    "#cbi-firewall-forwards .cbi-section-node { padding: 0; }",
    "#cbi-firewall-forwards table.cbi-section-table { width: 100%; border-collapse: collapse; margin: 0 0 12px; }",
    "#cbi-firewall-forwards table.cbi-section-table th {",
    "	padding: 10px 14px; font-size: 13px; font-weight: 600; color: var(--fw-muted); border-bottom: 1px solid var(--fw-border); text-align: left;",
    "}",
    "#cbi-firewall-forwards table.cbi-section-table td {",
    "	padding: 12px 14px; font-size: 13px; color: var(--fw-text); border-bottom: 1px solid var(--fw-border); vertical-align: middle;",
    "}",
    "#cbi-firewall-forwards table.cbi-section-table tr:hover td { background: var(--fw-soft); }",
    "#cbi-firewall-forwards .zonebadge {",
    "	display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; margin-right: 4px;",
    "}",
    "#cbi-firewall-forwards var { font-family: monospace; font-style: normal; font-weight: 600; color: var(--fw-accent); }",
    "#cbi-firewall-forwards .cbi-button-add {",
    "	background: var(--fw-accent) !important; border: 1px solid var(--fw-accent) !important; color: #fff !important;",
    "	padding: 6px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all .15s ease;",
    "}",
    "#cbi-firewall-forwards .cbi-button-add:hover { filter: brightness(1.08); }",
    "/* 底部操作区统一收纳在右下方 */",
    "#cbi-firewall-forwards .cbi-page-actions {",
    "	display: flex; justify-content: flex-end; align-items: center; gap: 12px; margin: 20px 0 0; padding: 18px 0 0;",
    "	border-top: 1px solid var(--fw-border); background: none; border-radius: 0; box-shadow: none;",
    "}",
    "#cbi-firewall-forwards .cbi-page-actions .cbi-button {",
    "	min-width: 110px; height: 36px; padding: 0 18px; border-radius: 8px; font-size: 13px; font-weight: 600;",
    "	margin: 0; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: all .15s ease;",
    "}",
    "#cbi-firewall-forwards .cbi-page-actions .cbi-button-apply, #cbi-firewall-forwards .cbi-page-actions .cbi-button-save {",
    "	background: var(--fw-accent) !important; border: 1px solid var(--fw-accent) !important; color: #fff !important;",
    "	box-shadow: 0 2px 6px rgba(94, 114, 228, .25);",
    "}",
    "#cbi-firewall-forwards .cbi-page-actions .cbi-button-apply:hover, #cbi-firewall-forwards .cbi-page-actions .cbi-button-save:hover { filter: brightness(1.08); }",
    "#cbi-firewall-forwards .cbi-page-actions .cbi-button-reset {",
    "	background: rgba(245, 54, 92, .08) !important; border: 1px solid rgba(245, 54, 92, .2) !important; color: var(--fw-danger) !important;",
    "}",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)

new_render = (
    "\t\treturn m.render().then(function(mapEl) {\n"
    "\t\t\tmapEl.setAttribute('id', 'cbi-firewall-forwards');\n"
    "\t\t\tif (!mapEl.querySelector('style[data-ui-skin=\"forwards\"]')) {\n"
    "\t\t\t\tvar css = '' +\n"
    + css_js + ";\n"
    "\t\t\t\tmapEl.insertBefore(E('style', { 'data-ui-skin': 'forwards' }, [ css ]), mapEl.firstChild);\n"
    "\t\t\t}\n"
    "\t\t\tvar h2 = mapEl.querySelector(':scope > h2');\n"
    "\t\t\tvar descr = mapEl.querySelector(':scope > .cbi-map-descr');\n"
    "\t\t\tif (h2 && descr && !mapEl.querySelector('.forwards-head')) {\n"
    "\t\t\t\tvar head = E('div', { 'class': 'forwards-head' }, [\n"
    "\t\t\t\t\tE('div', { 'class': 'forwards-head-left' }, [ h2.cloneNode(true) ]),\n"
    "\t\t\t\t\tE('div', { 'class': 'forwards-head-right' }, [ descr.cloneNode(true) ])\n"
    "\t\t\t\t]);\n"
    "\t\t\t\th2.remove();\n"
    "\t\t\t\tdescr.remove();\n"
    "\t\t\t\tmapEl.insertBefore(head, mapEl.firstChild.nextSibling);\n"
    "\t\t\t}\n"
    "\t\t\treturn mapEl;\n"
    "\t\t});\n"
    "\t}\n"
    "});"
)

if old_render not in t:
    raise SystemExit("forwards.js: return m.render() anchor not found")

t = t.replace(old_render, new_render, 1)

for must in ("forwards-head", "data-ui-skin", "#cbi-firewall-forwards"):
    if must not in t:
        raise SystemExit(f"forwards.js missing {must}")

p.write_text(t, encoding="utf-8")
print(f"OK    forwards.js skinned ({p})")
