#!/usr/bin/env python3
"""
luci-mod-system dropbear.js (SSH Access) 页面样式卡片化换皮
- 顶部白卡头 .dropbear-head 统一标题与说明
- 实例表单卡片化、右下角操作栏
"""

from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-dropbear" in t:
    print("SKIP  dropbear.js: already skinned")
    raise SystemExit(0)

old_render = "\t\treturn m.render();"

css_lines = [
    "#cbi-dropbear {",
    "	--db-accent: #5e72e4; --db-ok: #2dce89; --db-warn: #fb6340; --db-danger: #f5365c; --db-border: #e9ecef;",
    "	--db-muted: #8898aa; --db-text: #32325d; --db-card: #fff; --db-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-dropbear { --db-border:#3a3a3d; --db-muted:#9aa2ad; --db-text:#d7dae0; --db-card:#232324; --db-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-dropbear { --db-border:#3a3a3d; --db-muted:#9aa2ad; --db-text:#d7dae0; --db-card:#232324; --db-soft:#2b2b2d; } }',
    "#cbi-dropbear.cbi-map, #cbi-dropbear .cbi-map { padding: 0; margin: 0; }",
    "#cbi-dropbear .dropbear-head {",
    "	display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px 20px;",
    "	padding: 18px 24px; margin: 0 0 16px; background: var(--db-card); border: 1px solid var(--db-border);",
    "	border-radius: 12px; box-shadow: 0 2px 12px rgba(50,50,93,.06);",
    "}",
    "#cbi-dropbear .dropbear-head-left h2 { margin: 0; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--db-text); }",
    "#cbi-dropbear .dropbear-head-right .cbi-map-descr { margin: 0; font-size: 13px; line-height: 1.5; color: var(--db-muted); max-width: 540px; text-align: right; }",
    "@media (max-width: 768px) { #cbi-dropbear .dropbear-head-right .cbi-map-descr { text-align: left; } }",
    "#cbi-dropbear .cbi-section {",
    "	background: var(--db-card); border: 1px solid var(--db-border); border-radius: 12px;",
    "	box-shadow: 0 2px 12px rgba(50,50,93,.06); padding: 22px 26px; margin: 0 0 16px; box-sizing: border-box;",
    "}",
    "#cbi-dropbear .cbi-section-node { padding: 0; }",
    "#cbi-dropbear .cbi-value {",
    "	display: flex; align-items: flex-start; gap: 16px; flex-wrap: wrap; padding: 14px 0; margin: 0;",
    "	border-top: 1px solid var(--db-border);",
    "}",
    "#cbi-dropbear .cbi-value:first-child { border-top: 0; padding-top: 0; }",
    "#cbi-dropbear .cbi-value-title { width: 170px; flex-shrink: 0; margin: 0; padding: 8px 0 0; font-size: 13px; font-weight: 600; color: var(--db-text); text-align: left; }",
    "#cbi-dropbear .cbi-value-field { flex: 1; min-width: 240px; text-align: left; }",
    "#cbi-dropbear .cbi-input-text, #cbi-dropbear .cbi-input-select, #cbi-dropbear select {",
    "	width: 100%; max-width: 320px; box-sizing: border-box; padding: 8px 12px; border: 1px solid var(--db-border);",
    "	border-radius: 8px; background: var(--db-soft); color: var(--db-text); font-size: 13px;",
    "	transition: border-color .15s ease, box-shadow .15s ease;",
    "}",
    "#cbi-dropbear .cbi-input-text:focus, #cbi-dropbear .cbi-input-select:focus, #cbi-dropbear select:focus {",
    "	border-color: var(--db-accent); outline: 0; box-shadow: 0 0 0 3px rgba(94, 114, 228, .15);",
    "}",
    "#cbi-dropbear .cbi-input-checkbox { accent-color: var(--db-accent); width: 18px; height: 18px; cursor: pointer; margin-top: 6px; }",
    "#cbi-dropbear .cbi-value-description { margin: 6px 0 0; font-size: 13px; line-height: 1.6; color: var(--db-muted); }",
    "/* 底部操作区统一收纳在右下方 */",
    "#cbi-dropbear .cbi-page-actions {",
    "	display: flex; justify-content: flex-end; align-items: center; gap: 12px; margin: 20px 0 0; padding: 18px 0 0;",
    "	border-top: 1px solid var(--db-border); background: none; border-radius: 0; box-shadow: none;",
    "}",
    "#cbi-dropbear .cbi-page-actions .cbi-button {",
    "	min-width: 110px; height: 36px; padding: 0 18px; border-radius: 8px; font-size: 13px; font-weight: 600;",
    "	margin: 0; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; transition: all .15s ease;",
    "}",
    "#cbi-dropbear .cbi-page-actions .cbi-button-apply, #cbi-dropbear .cbi-page-actions .cbi-button-save {",
    "	background: var(--db-accent) !important; border: 1px solid var(--db-accent) !important; color: #fff !important;",
    "	box-shadow: 0 2px 6px rgba(94, 114, 228, .25);",
    "}",
    "#cbi-dropbear .cbi-page-actions .cbi-button-apply:hover, #cbi-dropbear .cbi-page-actions .cbi-button-save:hover { filter: brightness(1.08); }",
    "#cbi-dropbear .cbi-page-actions .cbi-button-reset {",
    "	background: rgba(245, 54, 92, .08) !important; border: 1px solid rgba(245, 54, 92, .2) !important; color: var(--db-danger) !important;",
    "}",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)

new_render = (
    "\t\treturn m.render().then(function(mapEl) {\n"
    "\t\t\tmapEl.setAttribute('id', 'cbi-dropbear');\n"
    "\t\t\tif (!mapEl.querySelector('style[data-ui-skin=\"dropbear\"]')) {\n"
    "\t\t\t\tvar css = '' +\n"
    + css_js + ";\n"
    "\t\t\t\tmapEl.insertBefore(E('style', { 'data-ui-skin': 'dropbear' }, [ css ]), mapEl.firstChild);\n"
    "\t\t\t}\n"
    "\t\t\tvar h2 = mapEl.querySelector(':scope > h2');\n"
    "\t\t\tvar descr = mapEl.querySelector(':scope > .cbi-map-descr');\n"
    "\t\t\tif (h2 && descr && !mapEl.querySelector('.dropbear-head')) {\n"
    "\t\t\t\tvar head = E('div', { 'class': 'dropbear-head' }, [\n"
    "\t\t\t\t\tE('div', { 'class': 'dropbear-head-left' }, [ h2.cloneNode(true) ]),\n"
    "\t\t\t\t\tE('div', { 'class': 'dropbear-head-right' }, [ descr.cloneNode(true) ])\n"
    "\t\t\t\t]);\n"
    "\t\t\t\th2.remove();\n"
    "\t\t\t\tdescr.remove();\n"
    "\t\t\t\tmapEl.insertBefore(head, mapEl.firstChild.nextSibling);\n"
    "\t\t\t}\n"
    "\t\t\treturn mapEl;\n"
    "\t\t});"
)

if old_render not in t:
    raise SystemExit("dropbear.js: return m.render() anchor not found")

t = t.replace(old_render, new_render, 1)

for must in ("dropbear-head", "data-ui-skin", "#cbi-dropbear"):
    if must not in t:
        raise SystemExit(f"dropbear.js missing {must}")

p.write_text(t, encoding="utf-8")
print(f"OK    dropbear.js skinned ({p})")
