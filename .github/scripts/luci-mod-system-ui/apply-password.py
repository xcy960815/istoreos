#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-password" in t:
    print("SKIP  password.js: already skinned")
    raise SystemExit(0)

old = "\t\treturn m.render();\n\t},"
if old not in t:
    raise SystemExit("password.js: return m.render() anchor not found")

for must in ("callSetPassword", "checkPassword", "Router Password", "pw1", "pw2", "handleSave"):
    if must not in t:
        raise SystemExit(f"password.js precheck missing {must}")

css_lines = [
    "#cbi-password {",
    "	--pw-accent: #5e72e4; --pw-ok: #2dce89; --pw-warn: #fb6340; --pw-danger: #f5365c; --pw-border: #e9ecef;",
    "	--pw-muted: #8898aa; --pw-text: #32325d; --pw-card: #fff; --pw-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-password { --pw-border:#3a3a3d; --pw-muted:#9aa2ad; --pw-text:#d7dae0; --pw-card:#232324; --pw-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-password { --pw-border:#3a3a3d; --pw-muted:#9aa2ad; --pw-text:#d7dae0; --pw-card:#232324; --pw-soft:#2b2b2d; } }',
    "#cbi-password.cbi-map, #cbi-password .cbi-map { padding: 0; margin: 0; }",
    "#cbi-password .password-head {",
    "	display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 8px 16px;",
    "	padding: 18px 22px; margin: 0 0 16px; background: var(--pw-card); border: 1px solid var(--pw-border);",
    "	border-radius: 12px; box-shadow: 0 2px 12px rgba(50,50,93,.06);",
    "}",
    "#cbi-password .password-head h2 { margin: 0; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--pw-text); }",
    "#cbi-password .password-head .cbi-map-descr { margin: 0; font-size: 13px; line-height: 1.6; color: var(--pw-muted); }",
    "#cbi-password .cbi-section {",
    "	background: var(--pw-card); border: 1px solid var(--pw-border); border-radius: 12px;",
    "	box-shadow: 0 2px 12px rgba(50,50,93,.06); padding: 24px 26px; margin: 0 0 16px; width: 100%; box-sizing: border-box;",
    "}",
    "#cbi-password .cbi-section-node { padding: 0; }",
    "#cbi-password .cbi-value {",
    "	display: flex; align-items: flex-start; gap: 16px; flex-wrap: wrap; padding: 14px 0; margin: 0;",
    "	border-top: 1px solid var(--pw-border); border-bottom: 0;",
    "}",
    "#cbi-password .cbi-value:first-child { border-top: 0; padding-top: 0; }",
    "#cbi-password .cbi-value-title { width: 140px; flex-shrink: 0; margin: 0; padding: 8px 0 0; font-size: 13px; font-weight: 600; color: var(--pw-text); text-align: left; }",
    "#cbi-password .cbi-value-field { flex: 1; min-width: 240px; text-align: left; }",
    "#cbi-password .cbi-input-text {",
    "	width: 100%; max-width: 320px; box-sizing: border-box; padding: 8px 12px; border: 1px solid var(--pw-border);",
    "	border-radius: 8px; background: var(--pw-soft); color: var(--pw-text); font-size: 14px;",
    "	transition: border-color .15s ease, box-shadow .15s ease;",
    "}",
    "#cbi-password .cbi-input-text:focus { border-color: var(--pw-accent); outline: 0; box-shadow: 0 0 0 3px rgba(94, 114, 228, .15); }",
    "#cbi-password .cbi-value-description { margin: 8px 0 0; font-size: 13px; line-height: 1.6; color: var(--pw-muted); }",
    "#cbi-password .cbi-value-description span {",
    "	display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;",
    "	margin-left: 6px; line-height: 1.4;",
    "}",
    '#cbi-password .cbi-value-description span[style*="green"] { background: rgba(45, 206, 137, .12) !important; color: var(--pw-ok) !important; border: 1px solid rgba(45, 206, 137, .25); }',
    '#cbi-password .cbi-value-description span[style*="orange"] { background: rgba(251, 99, 64, .12) !important; color: var(--pw-warn) !important; border: 1px solid rgba(251, 99, 64, .25); }',
    '#cbi-password .cbi-value-description span[style*="red"] { background: rgba(245, 54, 92, .12) !important; color: var(--pw-danger) !important; border: 1px solid rgba(245, 54, 92, .25); }',
    "#cbi-password .cbi-page-actions {",
    "	display: flex; justify-content: flex-end; gap: 10px; margin: 18px 0 0; padding: 16px 0 0;",
    "	border-top: 1px solid var(--pw-border); background: none; border-radius: 0;",
    "}",
    "#cbi-password .cbi-button-save {",
    "	min-width: 132px; height: 36px; padding: 0 20px; border-radius: 8px; font-size: 14px; font-weight: 600;",
    "	background: var(--pw-accent) !important; border: 1px solid var(--pw-accent) !important; color: #fff !important;",
    "	box-shadow: 0 2px 6px rgba(94, 114, 228, .25); cursor: pointer; display: inline-flex; align-items: center; justify-content: center;",
    "	transition: all .15s ease;",
    "}",
    "#cbi-password .cbi-button-save:hover { filter: brightness(1.08); }",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)

new = (
    "\t\treturn m.render().then(function(node) {\n"
    "\t\t\tnode.setAttribute('id', 'cbi-password');\n"
    "\t\t\tif (!node.querySelector('style[data-ui-skin=\"password\"]')) {\n"
    "\t\t\t\tvar css = '' +\n"
    + css_js + ";\n"
    "\t\t\t\tnode.insertBefore(E('style', { 'data-ui-skin': 'password' }, [ css ]), node.firstChild);\n"
    "\t\t\t}\n"
    "\t\t\tvar h2 = node.querySelector(':scope > h2');\n"
    "\t\t\tvar descr = node.querySelector(':scope > .cbi-map-descr');\n"
    "\t\t\tif (h2 && descr && !node.querySelector('.password-head')) {\n"
    "\t\t\t\tvar head = E('div', { 'class': 'password-head' }, [\n"
    "\t\t\t\t\tE('div', { 'class': 'password-head-title' }, [ h2.cloneNode(true) ]),\n"
    "\t\t\t\t\tE('div', { 'class': 'password-head-descr' }, [ descr.cloneNode(true) ])\n"
    "\t\t\t\t]);\n"
    "\t\t\t\th2.remove();\n"
    "\t\t\t\tdescr.remove();\n"
    "\t\t\t\tnode.insertBefore(head, node.firstChild.nextSibling);\n"
    "\t\t\t}\n"
    "\t\t\treturn node;\n"
    "\t\t});\n"
    "\t},"
)

t2 = t.replace(old, new, 1)
if t2 == t:
    raise SystemExit("password.js replace failed")

for must in ("callSetPassword", "checkPassword", "Router Password", "data-ui-skin", "#cbi-password", "password-head"):
    if must not in t2:
        raise SystemExit(f"password.js missing {must}")

p.write_text(t2, encoding="utf-8")
print(f"OK    password.js skinned ({p})")
