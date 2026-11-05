#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-flash" in t and "CBI.ContainerValue" in t:
    print("SKIP  flash.js: already skinned")
    raise SystemExit(0)
old = "\t\treturn m.render();\n\t},"
if old not in t:
    raise SystemExit("flash.js: return m.render() anchor not found")
for must in ("handleSysupgrade", "handleSysupgradeConfirm", "validate_firmware_image", "cgi-backup", "/tmp/firmware.bin", "mtdselect"):
    if must not in t:
        raise SystemExit(f"flash.js precheck missing {must}")

css_lines = [
"#cbi-flash {",
"	--flash-accent: #5e72e4; --flash-ok: #2dce89; --flash-warn: #fb6340; --flash-border: #e9ecef;",
"	--flash-muted: #8898aa; --flash-text: #32325d; --flash-card: #fff; --flash-soft: #f7f9fc;",
"}",
'body[theme="dark"] #cbi-flash { --flash-border:#3a3a3d; --flash-muted:#9aa2ad; --flash-text:#d7dae0; --flash-card:#232324; --flash-soft:#2b2b2d; }',
'@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-flash { --flash-border:#3a3a3d; --flash-muted:#9aa2ad; --flash-text:#d7dae0; --flash-card:#232324; --flash-soft:#2b2b2d; } }',
"#cbi-flash > h2 { margin:0 0 12px; font-size:18px; font-weight:600; line-height:1.3; color:var(--flash-text); }",
"#cbi-flash .cbi-map-descr { margin:0 0 16px; font-size:13px; line-height:1.6; color:var(--flash-muted); }",
"#cbi-flash .cbi-tabmenu { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 16px; padding:6px; border:1px solid var(--flash-border); border-radius:10px; background:var(--flash-soft); list-style:none; }",
"#cbi-flash .cbi-tabmenu > li { margin:0; border:0; background:none; }",
"#cbi-flash .cbi-tabmenu > li > a { display:inline-block; padding:6px 16px; border-radius:8px; font-size:13px; font-weight:600; color:var(--flash-muted); text-decoration:none; }",
"#cbi-flash .cbi-tabmenu > li.cbi-tab > a { background:var(--flash-accent); color:#fff; }",
"#cbi-flash .cbi-section[data-tab=\"actions\"] { background:none; border:0; box-shadow:none; padding:0; margin:0; }",
"#cbi-flash .cbi-section[data-tab=\"actions\"] > h3 { display:none; }",
"#cbi-flash #cbi-json-actions { padding:0; margin:0; border:0; background:none; box-shadow:none; }",
"#cbi-flash .cbi-value[data-widget=\"CBI.ContainerValue\"] { display:block; padding:0; margin:0 0 16px; border:0; background:none; }",
"#cbi-flash .cbi-value[data-widget=\"CBI.ContainerValue\"]:last-child { margin-bottom:0; }",
"#cbi-flash .cbi-value[data-widget=\"CBI.ContainerValue\"] > .cbi-section,",
"#cbi-flash .cbi-value[data-widget=\"CBI.ContainerValue\"] .cbi-section,",
"#cbi-flash .cbi-section[data-tab=\"config\"] {",
"	background:var(--flash-card); border:1px solid var(--flash-border); border-radius:12px;",
"	box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px;",
"}",
"#cbi-flash .cbi-section > h3, #cbi-flash .cbi-section-title { margin:0 0 6px; font-size:16px; font-weight:600; line-height:1.3; color:var(--flash-text); }",
"#cbi-flash .cbi-section-descr { margin:0 0 14px; font-size:13px; line-height:1.6; color:var(--flash-muted); }",
"#cbi-flash .cbi-section-node .cbi-value:not([data-widget=\"CBI.ContainerValue\"]) {",
"	display:flex; align-items:flex-start; gap:16px; flex-wrap:wrap;",
"	padding:12px 0; margin:0; border-top:1px solid var(--flash-border); border-bottom:0;",
"}",
"#cbi-flash .cbi-section-node .cbi-value:not([data-widget=\"CBI.ContainerValue\"]):first-child { padding-top:4px; border-top:0; }",
"#cbi-flash .cbi-section-node .cbi-value:not([data-widget=\"CBI.ContainerValue\"]):last-child { padding-bottom:2px; }",
"#cbi-flash .cbi-section-node .cbi-value[data-name=\"editlist\"] { display:block; padding-top:12px; }",
"#cbi-flash .cbi-value-title { width:190px; flex-shrink:0; margin:0; padding:8px 0 0; font-size:13px; font-weight:600; color:var(--flash-text); text-align:left; }",
"#cbi-flash .cbi-value-field { flex:1; min-width:220px; text-align:left; }",
"#cbi-flash .cbi-value-description { margin:8px 0 0; font-size:12px; line-height:1.6; color:var(--flash-muted); }",
"#cbi-flash .cbi-button, #cbi-flash .btn { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; font-weight:600; }",
"#cbi-flash textarea, #cbi-flash .cbi-input-textarea {",
"	width:100%; box-sizing:border-box; padding:14px 16px; border:1px solid var(--flash-border); border-radius:10px;",
"	background:var(--flash-soft); color:var(--flash-text);",
"	font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; line-height:1.6;",
"}",
"#cbi-flash .cbi-page-actions { display:flex; justify-content:flex-end; gap:10px; margin:14px 0 0; padding:14px 0 0; border-top:1px solid var(--flash-border); background:none; }",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)
new = (
    "\t\treturn m.render().then(function(node) {\n"
    "\t\t\tnode.setAttribute('id', 'cbi-flash');\n"
    "\t\t\tif (!node.querySelector('style[data-ui-skin=\"flash\"]')) {\n"
    "\t\t\t\tvar css = '' +\n"
    + css_js + ";\n"
    "\t\t\t\tnode.insertBefore(E('style', { 'data-ui-skin': 'flash' }, [ css ]), node.firstChild);\n"
    "\t\t\t}\n"
    "\t\t\treturn node;\n"
    "\t\t});\n"
    "\t},"
)
t2 = t.replace(old, new, 1)
if t2 == t:
    raise SystemExit("flash.js replace failed")
for must in ("handleSysupgrade", "handleSysupgradeConfirm", "validate_firmware_image", "handleBackup", "handleRestore", "handleFirstboot", "handleBlock", "mtdselect", "/tmp/firmware.bin", "data-ui-skin", "#cbi-flash", "dl_backup", "CBI.ContainerValue"):
    if must not in t2:
        raise SystemExit(f"flash.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    flash.js skinned ({p})")
