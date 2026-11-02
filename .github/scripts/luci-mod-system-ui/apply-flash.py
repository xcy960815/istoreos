#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-flash" in t:
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
"	--flash-accent: #5e72e4; --flash-warn: #fb6340; --flash-border: #e9ecef;",
"	--flash-muted: #8898aa; --flash-text: #32325d; --flash-card: #fff; --flash-soft: #f7f9fc;",
"}",
"#cbi-flash > h2 { margin:0 0 6px; font-size:18px; font-weight:600; line-height:1.3; color:var(--flash-text); }",
"#cbi-flash .cbi-map-descr { margin:0 0 16px; font-size:13px; line-height:1.6; color:var(--flash-muted); }",
'body[theme="dark"] #cbi-flash { --flash-border:#3a3a3d; --flash-muted:#9aa2ad; --flash-text:#d7dae0; --flash-card:#232324; --flash-soft:#2b2b2d; }',
'@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-flash { --flash-border:#3a3a3d; --flash-muted:#9aa2ad; --flash-text:#d7dae0; --flash-card:#232324; --flash-soft:#2b2b2d; } }',
"#cbi-flash .cbi-section {",
"	background: var(--flash-card); border: 1px solid var(--flash-border); border-radius: 12px;",
"	box-shadow: 0 2px 12px rgba(50, 50, 93, .06); padding: 16px 18px; margin: 0 0 16px;",
"}",
"#cbi-flash .cbi-section > h3, #cbi-flash .cbi-section-title {",
"	font-size: 16px; font-weight: 600; color: var(--flash-text);",
"}",
"#cbi-flash .cbi-section-descr { font-size: 13px; line-height: 1.6; color: var(--flash-muted); }",
"#cbi-flash .cbi-page-actions .cbi-button { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; }",
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
for must in ("handleSysupgrade", "handleSysupgradeConfirm", "validate_firmware_image", "handleBackup", "handleRestore", "handleFirstboot", "handleBlock", "mtdselect", "/tmp/firmware.bin", "data-ui-skin", "#cbi-flash", "dl_backup"):
    if must not in t2:
        raise SystemExit(f"flash.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    flash.js shell skinned ({p})")
