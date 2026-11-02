#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-reboot" in t:
    print("SKIP  reboot.js: already skinned")
    raise SystemExit(0)

old = """\trender: function(changes) {
\t\tvar body = E([
\t\t\tE('h2', _('Reboot')),
\t\t\tE('p', {}, _('Reboots the operating system of your device'))
\t\t]);

\t\tfor (var config in (changes || {})) {
\t\t\tbody.appendChild(E('p', { 'class': 'alert-message warning' },
\t\t\t\t_('Warning: There are unsaved changes that will get lost on reboot!')));
\t\t\tbreak;
\t\t}

\t\tbody.appendChild(E('hr'));
\t\tbody.appendChild(E('button', {
\t\t\t'class': 'cbi-button cbi-button-action important',
\t\t\t'click': ui.createHandlerFn(this, 'handleReboot')
\t\t}, _('Perform reboot')));

\t\treturn body;
\t},"""
if old not in t:
    raise SystemExit("reboot.js: render() anchor not found")

css_lines = [
"#cbi-reboot {",
"	--reboot-accent: #5e72e4; --reboot-warn: #fb6340; --reboot-border: #e9ecef;",
"	--reboot-muted: #8898aa; --reboot-text: #32325d; --reboot-card: #fff; --reboot-soft: #f7f9fc;",
"}",
"#cbi-reboot.cbi-section, #cbi-reboot .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0; }",
'body[theme="dark"] #cbi-reboot { --reboot-border:#3a3a3d; --reboot-muted:#9aa2ad; --reboot-text:#d7dae0; --reboot-card:#232324; --reboot-soft:#2b2b2d; }',
'@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-reboot { --reboot-border:#3a3a3d; --reboot-muted:#9aa2ad; --reboot-text:#d7dae0; --reboot-card:#232324; --reboot-soft:#2b2b2d; } }',
"#cbi-reboot .reboot-card { background:var(--reboot-card); border:1px solid var(--reboot-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px; }",
"#cbi-reboot .reboot-title { margin:0; font-size:18px; font-weight:600; line-height:1.3; color:var(--reboot-text); }",
"#cbi-reboot .reboot-sub { margin:6px 0 0; font-size:13px; line-height:1.6; color:var(--reboot-muted); }",
"#cbi-reboot .reboot-warn { margin:14px 0 0; padding:10px 12px; border-radius:10px; background:rgba(251,99,64,.08); color:var(--reboot-warn); font-size:13px; }",
"#cbi-reboot .reboot-actions { margin-top:18px; }",
"#cbi-reboot .reboot-btn { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; }",
]
css_js = " +\n".join("\t\t\t\t" + repr(line + "\n") for line in css_lines)
new = (
"""\trender: function(changes) {
\t\tvar warn = null;
\t\tfor (var config in (changes || {})) {
\t\t\twarn = E('p', { 'class': 'reboot-warn' },
\t\t\t\t_('Warning: There are unsaved changes that will get lost on reboot!'));
\t\t\tbreak;
\t\t}

\t\tvar css = '' +
"""
    + css_js
    + """;

\t\treturn E('div', { 'id': 'cbi-reboot', 'class': 'cbi-map' }, [
\t\t\tE('style', { 'data-ui-skin': 'reboot' }, [ css ]),
\t\t\tE('div', { 'class': 'cbi-section' }, [
\t\t\t\tE('div', { 'class': 'reboot-card' }, [
\t\t\t\t\tE('h2', { 'class': 'reboot-title' }, _('Reboot')),
\t\t\t\t\tE('p', { 'class': 'reboot-sub' }, _('Reboots the operating system of your device')),
\t\t\t\t\twarn,
\t\t\t\t\tE('div', { 'class': 'reboot-actions' }, [
\t\t\t\t\t\tE('button', {
\t\t\t\t\t\t\t'class': 'cbi-button cbi-button-action important reboot-btn',
\t\t\t\t\t\t\t'click': ui.createHandlerFn(this, 'handleReboot')
\t\t\t\t\t\t}, _('Perform reboot'))
\t\t\t\t\t])
\t\t\t\t])
\t\t\t])
\t\t]);
\t},"""
)
t2 = t.replace(old, new, 1)
if t2 == t:
    raise SystemExit("reboot.js replace failed")
for must in ("#cbi-reboot", "handleReboot", "callReboot", "Perform reboot", "awaitReconnect", "data-ui-skin"):
    if must not in t2:
        raise SystemExit(f"reboot.js missing {must}")
p.write_text(t2, encoding="utf-8")
print(f"OK    reboot.js skinned ({p})")
