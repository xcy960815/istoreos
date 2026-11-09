#!/usr/bin/env python3
"""Skin Tailscale status_bar, login_status_div, and setting form cards (docs/UI-STYLE.md). Keep authkey/AuthURL patches."""
from pathlib import Path
import re
import sys

def _upgrade_login_bound(text: str) -> str:
    """Fix Running-state left-shift when an older status skin is already present."""
    if ".ts-login-bound" in text:
        return text
    pattern = re.compile(
        r"(\t\} else if \(loginStatus === \"Running\"\) \{\n)"
        r"\t\trenderHTML = String\.format\('<a class=\"ts-link\" href=\"%s\" target=\"_blank\" rel=\"noopener noreferrer\">%s</a>', "
        r"'https://login\.tailscale\.com/admin/machines', displayName\);\n"
        r"\t\trenderHTML \+= String\.format\('<br><a class=\"ts-linkbtn ts-linkbtn-warn\" id=\"logout_button\">%s</a>', "
        r"_\('Log out and Unbind'\)\);\n"
        r"(\t\} else \{)",
        re.M,
    )
    repl = (
        r"\1"
        r"\t\trenderHTML = String.format(\n"
        r"\t\t\t'<span class=\"ts-login-bound\"><a class=\"ts-link\" href=\"%s\" target=\"_blank\" rel=\"noopener noreferrer\">%s</a>' +\n"
        r"\t\t\t'<a class=\"ts-linkbtn ts-linkbtn-warn\" id=\"logout_button\">%s</a></span>',\n"
        r"\t\t\t'https://login.tailscale.com/admin/machines', displayName, _('Log out and Unbind'));\n"
        r"\2"
    )
    text2, n = pattern.subn(repl, text, count=1)
    if n != 1:
        raise SystemExit("setting.js Running login branch not found for ts-login-bound upgrade")
    text = text2
    frag = "#login_status_div .ts-linkbtn-warn { color:var(--ts-warn); }\\n"
    add = "#login_status_div .ts-login-bound { display:flex; flex-direction:column; align-items:flex-start; gap:6px; max-width:100%; }\\n"
    if frag not in text:
        raise SystemExit("setting.js missing ts-linkbtn-warn CSS for ts-login-bound upgrade")
    if add not in text:
        text = text.replace(frag, frag + add, 1)
    print("setting.js Running login bound-align upgraded")
    return text


p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")

# --- 1) renderStatus + renderLogin + status_bar ---
if "ts-pill" not in t or "cbi-tailscale-status" not in t:
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
		/* .ts-login-bound keeps username+logout in a column. #login_status_div is
		   row-flex for title centering; a raw <br> inside that flex becomes a flex
		   item so the two links stay one wide row and Argon .cbi-value flex-wrap can
		   drop the whole field under the title (left of Port/Workdir inputs). */
		renderHTML = String.format(
			'<span class="ts-login-bound"><a class="ts-link" href="%s" target="_blank" rel="noopener noreferrer">%s</a>' +
			'<a class="ts-linkbtn ts-linkbtn-warn" id="logout_button">%s</a></span>',
			'https://login.tailscale.com/admin/machines', displayName, _('Log out and Unbind'));
	} else {
		renderHTML = String.format('<span class="ts-pill ts-pill-off"><span class="ts-dot"></span>%s</span>', _('NOT RUNNING'));
	}

	return renderHTML;
}"""
    t = t[: m.start()] + new_login + t[m.end() :]

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
        "#login_status_div .ts-login-bound { display:flex; flex-direction:column; align-items:flex-start; gap:6px; max-width:100%; }",
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
else:
    print("setting.js status/login skin already applied")

t = _upgrade_login_bound(t)

# --- 2) Form sections + tabs + page actions skin (#cbi-tailscale-setting) ---
if 'data-ui-skin="tailscale-form"' not in t or "#cbi-tailscale-setting" not in t:
    old_ret = "\t\treturn m.render();\n\t}"
    if old_ret not in t:
        raise SystemExit("setting.js return m.render() anchor not found")
    form_css_lines = [
        "#cbi-tailscale-setting {",
        "	--ts-accent: #5e72e4; --ts-ok: #2dce89; --ts-warn: #fb6340; --ts-border: #e9ecef;",
        "	--ts-muted: #8898aa; --ts-text: #32325d; --ts-card: #fff; --ts-soft: #f7f9fc;",
        "}",
        'body[theme="dark"] #cbi-tailscale-setting { --ts-border:#3a3a3d; --ts-muted:#9aa2ad; --ts-text:#d7dae0; --ts-card:#232324; --ts-soft:#2b2b2d; }',
        '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-tailscale-setting { --ts-border:#3a3a3d; --ts-muted:#9aa2ad; --ts-text:#d7dae0; --ts-card:#232324; --ts-soft:#2b2b2d; } }',
        "#cbi-tailscale-setting > h2 { margin:0 0 6px; font-size:18px; font-weight:600; line-height:1.3; color:var(--ts-text); }",
        "#cbi-tailscale-setting .cbi-map-descr { margin:0 0 16px; font-size:13px; line-height:1.6; color:var(--ts-muted); }",
        "#cbi-tailscale-setting .ts-head { display:flex; align-items:baseline; justify-content:space-between; gap:8px 16px; flex-wrap:wrap; margin:0 0 16px; padding:16px 22px; background:var(--ts-card); border:1px solid var(--ts-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); }",
        "#cbi-tailscale-setting .ts-head > h2 { margin:0; font-size:18px; font-weight:600; line-height:1.3; color:var(--ts-text); }",
        "#cbi-tailscale-setting .ts-head > .cbi-map-descr { margin:0 0 0 auto; font-size:13px; line-height:1.6; color:var(--ts-muted); text-align:right; }",
        "#cbi-tailscale-setting .cbi-section { background:var(--ts-card); border:1px solid var(--ts-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px; }",
        "#cbi-tailscale-setting .cbi-section > h3, #cbi-tailscale-setting .cbi-section-title { margin:0 0 6px; font-size:16px; font-weight:600; color:var(--ts-text); }",
        "#cbi-tailscale-setting .cbi-section-descr { margin:0 0 12px; font-size:13px; line-height:1.6; color:var(--ts-muted); }",
        "#cbi-tailscale-setting .cbi-tabmenu { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 14px; padding:6px; border:1px solid var(--ts-border); border-radius:10px; background:var(--ts-soft); list-style:none; }",
        "#cbi-tailscale-setting .cbi-tabmenu > li { margin:0; border:0; background:none; }",
        "#cbi-tailscale-setting .cbi-tabmenu > li > a { display:inline-block; padding:6px 14px; border-radius:8px; font-size:13px; font-weight:600; color:var(--ts-muted); text-decoration:none; }",
        "#cbi-tailscale-setting .cbi-tabmenu > li.cbi-tab > a { background:var(--ts-accent); color:#fff; }",
        "#cbi-tailscale-setting .cbi-value { padding:10px 0; border-bottom:1px solid var(--ts-border); }",
        "#cbi-tailscale-setting .cbi-value:last-child { border-bottom:0; padding-bottom:2px; }",
        "#cbi-tailscale-setting .cbi-value:first-child { padding-top:2px; }",
        "#cbi-tailscale-setting .cbi-value-title { color:var(--ts-text); font-size:13px; font-weight:600; }",
        "#cbi-tailscale-setting .cbi-value-description { color:var(--ts-muted); font-size:12px; line-height:1.6; }",
        "#cbi-tailscale-setting .cbi-value-description code, #cbi-tailscale-setting .cbi-section-descr code { padding:2px 6px; border-radius:6px; background:var(--ts-soft); font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; }",
        "#cbi-tailscale-setting .cbi-page-actions { margin-top:16px; padding:0; border:0; background:none; }",
        "#cbi-tailscale-setting .cbi-page-actions .cbi-button { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; }",
    ]
    form_css_js = " +\n".join("\t\t\t\t\t" + repr(line + "\n") for line in form_css_lines)
    new_ret = (
        "\t\treturn m.render().then(function(node) {\n"
        "\t\t\tnode.setAttribute('id', 'cbi-tailscale-setting');\n"
        "\t\t\tvar css = '' +\n"
        + form_css_js
        + ";\n"
        "\t\t\tvar skin = function() {\n"
        "\t\t\t\tvar h2 = null, descr = null, kids = node.children, i;\n"
        "\t\t\t\tfor (i = 0; i < kids.length; i++) {\n"
        "\t\t\t\t\tif (!h2 && kids[i].tagName === 'H2')\n"
        "\t\t\t\t\t\th2 = kids[i];\n"
        "\t\t\t\t\telse if (!descr && kids[i].classList && kids[i].classList.contains('cbi-map-descr'))\n"
        "\t\t\t\t\t\tdescr = kids[i];\n"
        "\t\t\t\t}\n"
        "\t\t\t\tif (h2 && descr && !node.querySelector('.ts-head')) {\n"
        "\t\t\t\t\tvar head = document.createElement('div');\n"
        "\t\t\t\t\thead.className = 'ts-head';\n"
        "\t\t\t\t\tnode.insertBefore(head, h2);\n"
        "\t\t\t\t\thead.appendChild(h2);\n"
        "\t\t\t\t\thead.appendChild(descr);\n"
        "\t\t\t\t}\n"
        "\t\t\t\tif (!node.querySelector('style[data-ui-skin=\"tailscale-form\"]'))\n"
        "\t\t\t\t\tnode.insertBefore(E('style', { 'data-ui-skin': 'tailscale-form' }, [ css ]), node.firstChild);\n"
        "\t\t\t};\n"
        "\t\t\tskin();\n"
        "\t\t\treturn node;\n"
        "\t\t});\n"
        "\t}"
    )
    t = t.replace(old_ret, new_ret, 1)
else:
    print("setting.js form skin already applied")

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
    "#cbi-tailscale-setting",
    "ts-head",
    'data-ui-skin="tailscale-form"',
    "service_status",
    "login_status_div",
    "ts-login-bound",
    "Waiting for auth URL",
    "noopener noreferrer",
    "parseStatus",
    "logout_button",
):
    if must not in t:
        raise SystemExit(f"setting.js skin missing {must}")
if "cbi-button-apply" in t:
    raise SystemExit("setting.js regressed to cbi-button-apply")

p.write_text(t, encoding="utf-8")
print(f"OK    setting.js status + form skinned ({p})")
