#!/usr/bin/env python3
"""
luci-mod-system sshkeys.js 页面样式卡片化换皮
- 顶部白卡头 .sshkeys-head 统一标题与说明
- 拖拽与粘贴添加密钥区 .sshkey-dropzone 卡片化
- 密钥项 .sshkey-item 凭据卡片化（算法胶囊、注释标题、等宽指纹、删除操作）
"""

from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-sshkeys" in t:
    print("SKIP  sshkeys.js: already skinned")
    raise SystemExit(0)

# 1. 替换 renderKeyItem
old_render_item = (
    "function renderKeyItem(pubkey) {\n"
    "\treturn E('div', {\n"
    "\t\tclass: 'item',\n"
    "\t\tclick: isReadonlyView ? null : removeKey,\n"
    "\t\t'data-key': pubkey.src\n"
    "\t}, [\n"
    "\t\tE('strong', {}, [ pubkey.comment || _('Unnamed key') ]), E('br'),\n"
    "\t\tE('small', {}, [\n"
    "\t\t\t'%s, %s'.format(pubkey.type, pubkey.curve || _('%d Bit').format(pubkey.bits)),\n"
    "\t\t\tpubkey.options ? E([], {}, [\n"
    "\t\t\t\t' / ', _('Options:'), ' ',\n"
    "\t\t\t\tE('code', {}, [Object.keys(pubkey.options).sort().join(', ')])\n"
    "\t\t\t]) : '',\n"
    "\t\t\tE('br'), E('code', {}, [pubkey.fprint])\n"
    "\t\t])\n"
    "\t]);\n"
    "}"
)

new_render_item = (
    "function renderKeyItem(pubkey) {\n"
    "\treturn E('div', {\n"
    "\t\tclass: 'item sshkey-item',\n"
    "\t\tclick: isReadonlyView ? null : removeKey,\n"
    "\t\t'data-key': pubkey.src\n"
    "\t}, [\n"
    "\t\tE('div', { class: 'sshkey-main', 'data-key': pubkey.src }, [\n"
    "\t\t\tE('div', { class: 'sshkey-title-row', 'data-key': pubkey.src }, [\n"
    "\t\t\t\tE('span', { class: 'sshkey-algo-badge' }, [ pubkey.type + (pubkey.curve ? ' ' + pubkey.curve : (pubkey.bits ? ' ' + pubkey.bits + ' Bit' : '')) ]),\n"
    "\t\t\t\tE('strong', { class: 'sshkey-comment', 'data-key': pubkey.src }, [ pubkey.comment || _('Unnamed key') ])\n"
    "\t\t\t]),\n"
    "\t\t\tE('div', { class: 'sshkey-details', 'data-key': pubkey.src }, [\n"
    "\t\t\t\tE('code', { class: 'sshkey-fprint', 'data-key': pubkey.src }, [ pubkey.fprint ]),\n"
    "\t\t\t\tpubkey.options ? E('span', { class: 'sshkey-options' }, [\n"
    "\t\t\t\t\t' ', _('Options:'), ' ',\n"
    "\t\t\t\t\tE('code', {}, [Object.keys(pubkey.options).sort().join(', ')])\n"
    "\t\t\t\t]) : ''\n"
    "\t\t\t])\n"
    "\t\t]),\n"
    "\t\tisReadonlyView ? '' : E('button', {\n"
    "\t\t\tclass: 'cbi-button sshkey-del-btn',\n"
    "\t\t\ttitle: _('Delete key'),\n"
    "\t\t\t'data-key': pubkey.src\n"
    "\t\t}, [ '🗑' ])\n"
    "\t]);\n"
    "}"
)

if old_render_item not in t:
    raise SystemExit("sshkeys.js: renderKeyItem anchor not found")

t = t.replace(old_render_item, new_render_item, 1)

# 2. 替换 render
old_render = (
    "\t\treturn E('div', {}, [\n"
    "\t\t\tE('h2', _('SSH-Keys')),\n"
    "\t\t\tE('div', { 'class': 'cbi-section-descr' }, _('Public keys allow for passwordless SSH logins with higher security than plain passwords. In order to upload a new key to the device, paste an OpenSSH-compatible public key or drag a <code>.pub</code> file into the input field.')),\n"
    "\t\t\tE('div', { 'class': 'cbi-section-node' }, list)\n"
    "\t\t]);"
)

css_lines = [
    "#cbi-sshkeys {",
    "	--sk-accent: #5e72e4; --sk-ok: #2dce89; --sk-warn: #fb6340; --sk-danger: #f5365c; --sk-border: #e9ecef;",
    "	--sk-muted: #8898aa; --sk-text: #32325d; --sk-card: #fff; --sk-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-sshkeys { --sk-border:#3a3a3d; --sk-muted:#9aa2ad; --sk-text:#d7dae0; --sk-card:#232324; --sk-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-sshkeys { --sk-border:#3a3a3d; --sk-muted:#9aa2ad; --sk-text:#d7dae0; --sk-card:#232324; --sk-soft:#2b2b2d; } }',
    "#cbi-sshkeys.cbi-map, #cbi-sshkeys .cbi-map { padding: 0; margin: 0; }",
    "#cbi-sshkeys .sshkeys-head {",
    "	display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px 20px;",
    "	padding: 18px 24px; margin: 0 0 16px; background: var(--sk-card); border: 1px solid var(--sk-border);",
    "	border-radius: 12px; box-shadow: 0 2px 12px rgba(50,50,93,.06);",
    "}",
    "#cbi-sshkeys .sshkeys-head-left h2 { margin: 0; font-size: 18px; font-weight: 600; line-height: 1.3; color: var(--sk-text); }",
    "#cbi-sshkeys .sshkeys-head-right .cbi-map-descr { margin: 0; font-size: 13px; line-height: 1.5; color: var(--sk-muted); max-width: 560px; text-align: right; }",
    "@media (max-width: 768px) { #cbi-sshkeys .sshkeys-head-right .cbi-map-descr { text-align: left; } }",
    "#cbi-sshkeys .cbi-section {",
    "	background: var(--sk-card); border: 1px solid var(--sk-border); border-radius: 12px;",
    "	box-shadow: 0 2px 12px rgba(50,50,93,.06); padding: 22px 24px; margin: 0 0 16px; box-sizing: border-box;",
    "}",
    "#cbi-sshkeys .cbi-section-node { padding: 0; }",
    "#cbi-sshkeys .cbi-dynlist { display: flex; flex-direction: column; gap: 12px; }",
    "/* 添加密钥输入框与操作 */",
    "#cbi-sshkeys .cbi-dynlist .add-item {",
    "	display: flex; gap: 10px; align-items: center; padding: 14px 16px; border: 2px dashed var(--sk-border);",
    "	border-radius: 10px; background: var(--sk-soft); box-sizing: border-box;",
    "}",
    "#cbi-sshkeys .cbi-dynlist .add-item input.cbi-input-text {",
    "	flex: 1; padding: 9px 14px; border: 1px solid var(--sk-border); border-radius: 8px;",
    "	background: var(--sk-card); color: var(--sk-text); font-size: 13px;",
    "	transition: border-color .15s ease, box-shadow .15s ease;",
    "}",
    "#cbi-sshkeys .cbi-dynlist .add-item input.cbi-input-text:focus {",
    "	border-color: var(--sk-accent); outline: 0; box-shadow: 0 0 0 3px rgba(94, 114, 228, .15);",
    "}",
    "#cbi-sshkeys .cbi-dynlist .add-item button.cbi-button {",
    "	height: 36px; padding: 0 18px; border-radius: 8px; font-size: 13px; font-weight: 600;",
    "	background: var(--sk-accent) !important; border: 1px solid var(--sk-accent) !important; color: #fff !important;",
    "	box-shadow: 0 2px 6px rgba(94, 114, 228, .2); cursor: pointer; white-space: nowrap;",
    "	transition: all .15s ease;",
    "}",
    "#cbi-sshkeys .cbi-dynlist .add-item button.cbi-button:hover { filter: brightness(1.08); }",
    "/* 密钥卡片项 */",
    "#cbi-sshkeys .sshkey-item {",
    "	display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 18px;",
    "	border: 1px solid var(--sk-border); border-radius: 10px; background: var(--sk-soft);",
    "	transition: all .15s ease; cursor: pointer;",
    "}",
    "#cbi-sshkeys .sshkey-item:hover { border-color: var(--sk-accent); background: var(--sk-card); box-shadow: 0 2px 8px rgba(94,114,228,.08); }",
    "#cbi-sshkeys .sshkey-main { flex: 1; min-width: 0; }",
    "#cbi-sshkeys .sshkey-title-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin: 0 0 6px; }",
    "#cbi-sshkeys .sshkey-algo-badge {",
    "	display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700;",
    "	background: rgba(94, 114, 228, .12); color: var(--sk-accent); border: 1px solid rgba(94, 114, 228, .25);",
    "}",
    "#cbi-sshkeys .sshkey-comment { font-size: 14px; color: var(--sk-text); }",
    "#cbi-sshkeys .sshkey-details { font-size: 12px; color: var(--sk-muted); line-height: 1.4; word-break: break-all; }",
    "#cbi-sshkeys .sshkey-fprint {",
    "	font-family: monospace; font-size: 12px; background: var(--sk-card); padding: 2px 6px; border-radius: 4px;",
    "	border: 1px solid var(--sk-border); color: var(--sk-text);",
    "}",
    "#cbi-sshkeys .sshkey-options { margin-left: 8px; }",
    "#cbi-sshkeys .sshkey-del-btn {",
    "	width: 34px; height: 34px; padding: 0; border-radius: 8px; font-size: 14px;",
    "	background: rgba(245, 54, 92, .08) !important; border: 1px solid rgba(245, 54, 92, .2) !important;",
    "	color: var(--sk-danger) !important; cursor: pointer; display: flex; align-items: center; justify-content: center;",
    "	transition: all .15s ease;",
    "}",
    "#cbi-sshkeys .sshkey-del-btn:hover { background: rgba(245, 54, 92, .18) !important; }",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)

new_render = (
    "\t\tvar css = '' +\n"
    + css_js + ";\n"
    "\t\treturn E('div', { 'id': 'cbi-sshkeys', 'class': 'cbi-map' }, [\n"
    "\t\t\tE('style', { 'data-ui-skin': 'sshkeys' }, [ css ]),\n"
    "\t\t\tE('div', { 'class': 'sshkeys-head' }, [\n"
    "\t\t\t\tE('div', { 'class': 'sshkeys-head-left' }, [ E('h2', {}, [ _('SSH-Keys') ]) ]),\n"
    "\t\t\t\tE('div', { 'class': 'sshkeys-head-right' }, [\n"
    "\t\t\t\t\tE('div', { 'class': 'cbi-map-descr' }, [\n"
    "\t\t\t\t\t\t_('Public keys allow for passwordless SSH logins with higher security than plain passwords. In order to upload a new key to the device, paste an OpenSSH-compatible public key or drag a <code>.pub</code> file into the input field.')\n"
    "\t\t\t\t\t])\n"
    "\t\t\t\t])\n"
    "\t\t\t]),\n"
    "\t\t\tE('div', { 'class': 'cbi-section' }, [\n"
    "\t\t\t\tE('div', { 'class': 'cbi-section-node' }, list)\n"
    "\t\t\t])\n"
    "\t\t]);"
)

if old_render not in t:
    raise SystemExit("sshkeys.js: render anchor not found")

t = t.replace(old_render, new_render, 1)

for must in ("SSHPubkeyDecoder", "sshkeys-head", "sshkey-item", "data-ui-skin", "#cbi-sshkeys"):
    if must not in t:
        raise SystemExit(f"sshkeys.js missing {must}")

p.write_text(t, encoding="utf-8")
print(f"OK    sshkeys.js skinned ({p})")
