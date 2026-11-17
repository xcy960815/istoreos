#!/usr/bin/env python3
"""
luci-mod-network dhcp.js 页面样式卡片化换皮
- 顶部白卡头 .dhcp-head 统一标题与说明
- 药丸切换标签 .cbi-tabmenu (Pill Tabs)
- 活跃 DHCP 租约卡片化、静态地址分配表格美化、右下角操作栏
"""

from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-dhcp" in t:
    print("SKIP  dhcp.js: already skinned")
    raise SystemExit(0)

old_render = (
    "\t\treturn m.render().then(function(mapEl) {\n"
    "\t\t\tpoll.add(function() {\n"
    "\t\t\t\treturn callDHCPLeases().then(function(leaseinfo) {"
)

css_lines = [
    "#cbi-dhcp {",
    "	--dhcp-accent: #5e72e4; --dhcp-ok: #2dce89; --dhcp-warn: #fb6340; --dhcp-danger: #f5365c; --dhcp-border: #e9ecef;",
    "	--dhcp-muted: #8898aa; --dhcp-text: #32325d; --dhcp-card: #fff; --dhcp-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-dhcp { --dhcp-border:#3a3a3d; --dhcp-muted:#9aa2ad; --dhcp-text:#d7dae0; --dhcp-card:#232324; --dhcp-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-dhcp { --dhcp-border:#3a3a3d; --dhcp-muted:#9aa2ad; --dhcp-text:#d7dae0; --dhcp-card:#232324; --dhcp-soft:#2b2b2d; } }',
    "#cbi-dhcp.cbi-map, #cbi-dhcp .cbi-map { padding: 0; margin: 0; }",
    "#cbi-dhcp .dhcp-head {",
    "	display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px 20px;",
    "	padding: 18px 24px; margin: 0 0 16px; background: var(--dhcp-card); border: 1px solid var(--dhcp-border);",
    "	border-radius: 12px; box-shadow: 0 2px 12px rgba(50,50,93,.06);",
    "}",
    "#cbi-dhcp .dhcp-head-left h2 { margin: 0; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--dhcp-text); }",
    "#cbi-dhcp .dhcp-head-right .cbi-map-descr { margin: 0; font-size: 13px; line-height: 1.5; color: var(--dhcp-muted); max-width: 540px; text-align: right; }",
    "@media (max-width: 768px) { #cbi-dhcp .dhcp-head-right .cbi-map-descr { text-align: left; } }",
    "/* 药丸标签栏 */",
    "#cbi-dhcp .cbi-tabmenu {",
    "	display: flex; gap: 8px; border: 0; padding: 0 0 14px; margin: 0 0 16px; list-style: none; overflow-x: auto;",
    "}",
    "#cbi-dhcp .cbi-tabmenu > li { margin: 0; padding: 0; list-style: none; }",
    "#cbi-dhcp .cbi-tabmenu > li > a {",
    "	display: inline-flex; align-items: center; padding: 7px 18px; border-radius: 999px; font-size: 13px; font-weight: 600;",
    "	background: var(--dhcp-card); border: 1px solid var(--dhcp-border); color: var(--dhcp-muted); text-decoration: none;",
    "	transition: all .15s ease;",
    "}",
    "#cbi-dhcp .cbi-tabmenu > li > a:hover { color: var(--dhcp-text); border-color: var(--dhcp-accent); }",
    "#cbi-dhcp .cbi-tabmenu > li.cbi-tab > a, #cbi-dhcp .cbi-tabmenu > li.active > a {",
    "	background: var(--dhcp-accent) !important; border-color: var(--dhcp-accent) !important; color: #fff !important;",
    "	box-shadow: 0 2px 8px rgba(94, 114, 228, .25);",
    "}",
    "/* 表单卡片化 */",
    "#cbi-dhcp .cbi-section {",
    "	background: var(--dhcp-card); border: 1px solid var(--dhcp-border); border-radius: 12px;",
    "	box-shadow: 0 2px 12px rgba(50,50,93,.06); padding: 22px 26px; margin: 0 0 16px; box-sizing: border-box;",
    "}",
    "#cbi-dhcp .cbi-section-node { padding: 0; }",
    "#cbi-dhcp .cbi-value {",
    "	display: flex; align-items: flex-start; gap: 16px; flex-wrap: wrap; padding: 14px 0; margin: 0;",
    "	border-top: 1px solid var(--dhcp-border);",
    "}",
    "#cbi-dhcp .cbi-value:first-child { border-top: 0; padding-top: 0; }",
    "#cbi-dhcp .cbi-value-title { width: 170px; flex-shrink: 0; margin: 0; padding: 8px 0 0; font-size: 13px; font-weight: 600; color: var(--dhcp-text); text-align: left; }",
    "#cbi-dhcp .cbi-value-field { flex: 1; min-width: 240px; text-align: left; }",
    "#cbi-dhcp .cbi-input-text, #cbi-dhcp .cbi-input-select, #cbi-dhcp select {",
    "	width: 100%; max-width: 380px; box-sizing: border-box; padding: 8px 12px; border: 1px solid var(--dhcp-border);",
    "	border-radius: 8px; background: var(--dhcp-soft); color: var(--dhcp-text); font-size: 13px;",
    "	transition: border-color .15s ease, box-shadow .15s ease;",
    "}",
    "#cbi-dhcp .cbi-input-text:focus, #cbi-dhcp .cbi-input-select:focus, #cbi-dhcp select:focus {",
    "	border-color: var(--dhcp-accent); outline: 0; box-shadow: 0 0 0 3px rgba(94, 114, 228, .15);",
    "}",
    "#cbi-dhcp .cbi-input-checkbox { accent-color: var(--dhcp-accent); width: 18px; height: 18px; cursor: pointer; margin-top: 6px; }",
    "#cbi-dhcp .cbi-value-description { margin: 6px 0 0; font-size: 13px; line-height: 1.6; color: var(--dhcp-muted); }",
    "/* 租约表格 */",
    "#cbi-dhcp table#lease_status_table, #cbi-dhcp table#lease6_status_table, #cbi-dhcp table.cbi-section-table {",
    "	width: 100%; border-collapse: collapse; margin: 12px 0;",
    "}",
    "#cbi-dhcp table th {",
    "	padding: 10px 14px; font-size: 13px; font-weight: 600; color: var(--dhcp-muted); border-bottom: 1px solid var(--dhcp-border); text-align: left;",
    "}",
    "#cbi-dhcp table td {",
    "	padding: 12px 14px; font-size: 13px; color: var(--dhcp-text); border-bottom: 1px solid var(--dhcp-border); vertical-align: middle;",
    "}",
    "#cbi-dhcp table tr:hover td { background: var(--dhcp-soft); }",
    "/* 底部操作区统一收纳在右下方 */",
    "#cbi-dhcp .cbi-page-actions {",
    "	display: flex; justify-content: flex-end; align-items: center; gap: 12px; margin: 20px 0 0; padding: 18px 0 0;",
    "	border-top: 1px solid var(--dhcp-border); background: none; border-radius: 0; box-shadow: none;",
    "}",
    "#cbi-dhcp .cbi-page-actions .cbi-button {",
    "	min-width: 110px; height: 36px; padding: 0 18px; border-radius: 8px; font-size: 13px; font-weight: 600;",
    "	margin: 0; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: all .15s ease;",
    "}",
    "#cbi-dhcp .cbi-page-actions .cbi-button-apply, #cbi-dhcp .cbi-page-actions .cbi-button-save {",
    "	background: var(--dhcp-accent) !important; border: 1px solid var(--dhcp-accent) !important; color: #fff !important;",
    "	box-shadow: 0 2px 6px rgba(94, 114, 228, .25);",
    "}",
    "#cbi-dhcp .cbi-page-actions .cbi-button-apply:hover, #cbi-dhcp .cbi-page-actions .cbi-button-save:hover { filter: brightness(1.08); }",
    "#cbi-dhcp .cbi-page-actions .cbi-button-reset {",
    "	background: rgba(245, 54, 92, .08) !important; border: 1px solid rgba(245, 54, 92, .2) !important; color: var(--dhcp-danger) !important;",
    "}",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)

new_render = (
    "\t\treturn m.render().then(function(mapEl) {\n"
    "\t\t\tmapEl.setAttribute('id', 'cbi-dhcp');\n"
    "\t\t\tif (!mapEl.querySelector('style[data-ui-skin=\"dhcp\"]')) {\n"
    "\t\t\t\tvar css = '' +\n"
    + css_js + ";\n"
    "\t\t\t\tmapEl.insertBefore(E('style', { 'data-ui-skin': 'dhcp' }, [ css ]), mapEl.firstChild);\n"
    "\t\t\t}\n"
    "\t\t\tvar h2 = mapEl.querySelector(':scope > h2');\n"
    "\t\t\tvar descr = mapEl.querySelector(':scope > .cbi-map-descr');\n"
    "\t\t\tif (h2 && descr && !mapEl.querySelector('.dhcp-head')) {\n"
    "\t\t\t\tvar head = E('div', { 'class': 'dhcp-head' }, [\n"
    "\t\t\t\t\tE('div', { 'class': 'dhcp-head-left' }, [ h2.cloneNode(true) ]),\n"
    "\t\t\t\t\tE('div', { 'class': 'dhcp-head-right' }, [ descr.cloneNode(true) ])\n"
    "\t\t\t\t]);\n"
    "\t\t\t\th2.remove();\n"
    "\t\t\t\tdescr.remove();\n"
    "\t\t\t\tmapEl.insertBefore(head, mapEl.firstChild.nextSibling);\n"
    "\t\t\t}\n"
    "\t\t\tpoll.add(function() {\n"
    "\t\t\t\treturn callDHCPLeases().then(function(leaseinfo) {"
)

if old_render not in t:
    raise SystemExit("dhcp.js: return m.render() anchor not found")

t = t.replace(old_render, new_render, 1)

for must in ("dhcp-head", "data-ui-skin", "#cbi-dhcp"):
    if must not in t:
        raise SystemExit(f"dhcp.js missing {must}")

p.write_text(t, encoding="utf-8")
print(f"OK    dhcp.js skinned ({p})")
