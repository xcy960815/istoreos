#!/usr/bin/env python3
"""Skin Tailscale status_bar + login_status_div only (docs/UI-STYLE.md). Keep authkey/AuthURL patches."""
from pathlib import Path
import re
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "ts-pill" in t and "cbi-tailscale-status" in t:
    print("setting.js status skin already applied")
    raise SystemExit(0)

# --- renderStatus ---
old_status = None
candidates = [
    """function renderStatus(isRunning) {
	const spanTemp = '<em><span style="color:%s"><strong>%s %s</strong></span></em>';
	let renderHTML;
	if (isRunning) {
		renderHTML = String.format(spanTemp, 'green', _('Tailscale'), _('RUNNING'));
	} else {
		renderHTML = String.format(spanTemp, 'red', _('Tailscale'), _('NOT RUNNING'));
	}

	return renderHTML;
}""",
    """function renderStatus(isRunning) {
	var spanTemp = '<em><span style="color:%s"><strong>%s %s</strong></span></em>';
	var renderHTML;
	if (isRunning) {
		renderHTML = String.format(spanTemp, 'green', _('Tailscale'), _('RUNNING'));
	} else {
		renderHTML = String.format(spanTemp, 'red', _('Tailscale'), _('NOT RUNNING'));
	}

	return renderHTML;
}""",
]
for c in candidates:
    if c in t:
        old_status = c
        break
if not old_status:
    raise SystemExit("setting.js renderStatus anchor not found")

new_status = """function renderStatus(isRunning) {
	if (isRunning) {
		return '<span class="ts-pill ts-pill-ok"><span class="ts-dot"></span>' +
			'%s %s'.format(_('Tailscale'), _('RUNNING')) + '</span>';
	}
	return '<span class="ts-pill ts-pill-off"><span class="ts-dot"></span>' +
		'%s %s'.format(_('Tailscale'), _('NOT RUNNING')) + '</span>';
}"""
t = t.replace(old_status, new_status, 1)

# --- renderLogin: replace whole function body variants ---
# After prior patch, NeedsLogin uses authURL branch + Waiting for auth URL.
login_re = re.compile(
    r"function renderLogin\(loginStatus, authURL, displayName\) \{.*?\n\treturn renderHTML;\n\}",
    re.S,
)
m = login_re.search(t)
if not m:
    raise SystemExit("setting.js renderLogin function not found")

new_login = """function renderLogin(loginStatus, authURL, displayName) {
	let renderHTML;
	if (loginStatus === "NeedsLogin") {
		if (authURL) {
			/* plain <a> keeps horizontal alignment with cbi-value-title; cbi-button floats in Argon */
			renderHTML = String.format('<a class="ts-linkbtn" href="%s" target="_blank" rel="noopener noreferrer">%s</a>', authURL, _('Need to log in'));
		} else {
			renderHTML = String.format('<span class="ts-pill ts-pill-wait"><span class="ts-dot"></span>%s</span>', _('Waiting for auth URL'));
		}
	} else if (loginStatus === "Running") {
		renderHTML = String.format('<a class="ts-link" href="%s" target="_blank" rel="noopener noreferrer">%s</a>', 'https://login.tailscale.com/admin/machines', displayName);
		renderHTML += String.format('<br><a class="ts-linkbtn ts-linkbtn-warn" id="logout_button">%s</a>', _('Log out and Unbind'));
	} else {
		renderHTML = String.format('<span class="ts-pill ts-pill-off"><span class="ts-dot"></span>%s</span>', _('NOT RUNNING'));
	}

	return renderHTML;
}"""
t = t[: m.start()] + new_login + t[m.end() :]

# --- status_bar wrap + CSS ---
bar_re = re.compile(
    r"return E\('div', \{ class: 'cbi-section', id: 'status_bar' \}, \[\s*"
    r"E\('p', \{ id: 'service_status' \}, _\('Collecting data \.\.\.'\)\)\s*"
    r"\]\);",
    re.M,
)
bm = bar_re.search(t)
if not bm:
    raise SystemExit("setting.js status_bar anchor not found")

css_lines = [
"#cbi-tailscale-status, #login_status_div {",
"	--ts-accent: #5e72e4; --ts-ok: #2dce89; --ts-warn: #fb6340; --ts-border: #e9ecef;",
"	--ts-muted: #8898aa; --ts-text: #32325d; --ts-card: #fff; --ts-soft: #f7f9fc;",
"}",
"#cbi-tailscale-status.cbi-section, #cbi-tailscale-status .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0; }",
'body[theme="dark"] #cbi-tailscale-status, body[theme="dark"] #login_status_div { --ts-border:#3a3a3d; --ts-muted:#9aa2ad; --ts-text:#d7dae0; --ts-card:#232324; --ts-soft:#2b2b2d; }',
'@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-tailscale-status, body[theme="normal"] #login_status_div { --ts-border:#3a3a3d; --ts-muted:#9aa2ad; --ts-text:#d7dae0; --ts-card:#232324; --ts-soft:#2b2b2d; } }',
"#cbi-tailscale-status .ts-card { background:var(--ts-card); border:1px solid var(--ts-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:16px 18px; margin:0 0 16px; }",
"#cbi-tailscale-status .ts-row { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }",
"#cbi-tailscale-status .ts-label { font-size:13px; color:var(--ts-muted); }",
"#cbi-tailscale-status .ts-pill, #login_status_div .ts-pill { display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px; background:var(--ts-soft); font-size:13px; font-weight:600; color:var(--ts-text); font-style:normal; }",
"#cbi-tailscale-status .ts-dot, #login_status_div .ts-dot { width:10px; height:10px; border-radius:50%; background:var(--ts-muted); box-shadow:0 0 0 4px rgba(136,152,170,.12); }",
"#cbi-tailscale-status .ts-pill-ok .ts-dot, #login_status_div .ts-pill-ok .ts-dot { background:var(--ts-ok); box-shadow:0 0 0 4px rgba(45,206,137,.12); }",
"#cbi-tailscale-status .ts-pill-off .ts-dot, #login_status_div .ts-pill-off .ts-dot { background:var(--ts-warn); box-shadow:0 0 0 4px rgba(251,99,64,.12); }",
"#cbi-tailscale-status .ts-pill-wait .ts-dot, #login_status_div .ts-pill-wait .ts-dot { background:var(--ts-warn); box-shadow:0 0 0 4px rgba(251,99,64,.12); }",
"#login_status_div .ts-linkbtn { color:var(--ts-warn); font-weight:600; text-decoration:underline; vertical-align:middle; cursor:pointer; }",
"#login_status_div .ts-link { color:var(--ts-accent); font-weight:600; text-decoration:underline; }",
"#login_status_div .ts-linkbtn-warn { color:var(--ts-warn); }",
"#cbi-tailscale-status #service_status, #login_status_div { margin:0; min-height:1.5em; }",
]
css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in css_lines)
new_bar = (
    "return E('div', { id: 'cbi-tailscale-status' }, [\n"
    "\t\t\t\tE('style', { 'data-ui-skin': 'tailscale-status' }, [ '' +\n"
    + css_js
    + " ]),\n"
    "\t\t\t\tE('div', { class: 'cbi-section', id: 'status_bar' }, [\n"
    "\t\t\t\t\tE('div', { class: 'ts-card' }, [\n"
    "\t\t\t\t\t\tE('div', { class: 'ts-row' }, [\n"
    "\t\t\t\t\t\t\tE('span', { class: 'ts-label' }, _('Service status')),\n"
    "\t\t\t\t\t\t\tE('p', { id: 'service_status' }, _('Collecting data ...'))\n"
    "\t\t\t\t\t\t])\n"
    "\t\t\t\t\t])\n"
    "\t\t\t\t])\n"
    "\t\t\t]);"
)
t = t[: bm.start()] + new_bar + t[bm.end() :]

# zh_Hans Service status
po = p.parents[4] / "po" / "zh_Hans" / "tailscale.po" if len(p.parents) > 4 else None
# setting.js is htdocs/luci-static/resources/view/tailscale/setting.js -> parents[5]=pkg?
po_path = None
for depth in range(3, 8):
    if depth >= len(p.parents):
        break
    cand = p.parents[depth] / "po" / "zh_Hans" / "tailscale.po"
    if cand.is_file():
        po_path = cand
        break
if po_path:
    po = po_path.read_text(encoding="utf-8")
    if 'msgid "Service status"' not in po:
        po += '\nmsgid "Service status"\nmsgstr "服务状态"\n'
        po_path.write_text(po, encoding="utf-8")
        print("zh_Hans added Service status")
    else:
        print("zh_Hans Service status present")
else:
    print("WARN  tailscale zh_Hans po not found")

for must in (
    "ts-pill",
    "cbi-tailscale-status",
    "service_status",
    "login_status_div",
    "Waiting for auth URL",
    "noopener noreferrer",
    "parseStatus",
    "logout_button",
):
    if must not in t:
        raise SystemExit(f"setting.js status skin missing {must}")
if "cbi-button-apply" in t:
    raise SystemExit("setting.js regressed to cbi-button-apply")

p.write_text(t, encoding="utf-8")
print(f"OK    setting.js status/login skinned ({p})")
