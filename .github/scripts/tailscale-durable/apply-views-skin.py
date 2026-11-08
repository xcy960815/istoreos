#!/usr/bin/env python3
"""Skin Tailscale interface.js + log.js (docs/UI-STYLE.md). Keep all load/poll/DOM ids intact."""
from pathlib import Path
import sys

iface_path = Path(sys.argv[1])
log_path = Path(sys.argv[2])

# --- 1) interface.js ---
t = iface_path.read_text(encoding="utf-8")
if "'data-ui-skin': 'tailscale-iface'" in t and "#cbi-tailscale-iface" in t:
    print("SKIP  tailscale interface.js: already skinned")
else:
    old_iface = """\trender(data) {
\t\tconst content = E([], [
\t\t\tE('h2', { class: 'content' }, _('Tailscale')),
\t\t\tE('div', { class: 'cbi-map-descr' }, _('Tailscale is a cross-platform and easy to use virtual LAN.')),
\t\t\tE('div')
\t\t]);
\t\tconst container = content.lastElementChild;

\t\tdom.content(container, this.renderContent(data));
\t\tthis.pollData(container);

\t\treturn content;
\t},"""
    if old_iface not in t:
        raise SystemExit("tailscale interface.js: render() anchor not found")
    iface_css = [
        "#cbi-tailscale-iface {",
        "	--tsi-accent: #5e72e4; --tsi-border: #e9ecef; --tsi-muted: #8898aa;",
        "	--tsi-text: #32325d; --tsi-card: #fff; --tsi-soft: #f7f9fc;",
        "}",
        "#cbi-tailscale-iface.cbi-section, #cbi-tailscale-iface .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0; }",
        'body[theme="dark"] #cbi-tailscale-iface { --tsi-border:#3a3a3d; --tsi-muted:#9aa2ad; --tsi-text:#d7dae0; --tsi-card:#232324; --tsi-soft:#2b2b2d; }',
        '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-tailscale-iface { --tsi-border:#3a3a3d; --tsi-muted:#9aa2ad; --tsi-text:#d7dae0; --tsi-card:#232324; --tsi-soft:#2b2b2d; } }',
        "#cbi-tailscale-iface > h2 { margin:0 0 6px; font-size:18px; font-weight:600; line-height:1.3; color:var(--tsi-text); }",
        "#cbi-tailscale-iface .cbi-map-descr { margin:0 0 16px; font-size:13px; line-height:1.6; color:var(--tsi-muted); }",
        "#cbi-tailscale-iface .ts-iface-head { display:flex; align-items:baseline; justify-content:space-between; gap:8px 16px; flex-wrap:wrap; margin:0 0 16px; padding:16px 22px; background:var(--tsi-card); border:1px solid var(--tsi-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); }",
        "#cbi-tailscale-iface .ts-iface-head > h2 { margin:0; font-size:18px; font-weight:600; line-height:1.3; color:var(--tsi-text); }",
        "#cbi-tailscale-iface .ts-iface-head > .cbi-map-descr { margin:0 0 0 auto; font-size:13px; line-height:1.6; color:var(--tsi-muted); text-align:right; }",
        "#cbi-tailscale-iface .ts-iface-card { background:var(--tsi-card); border:1px solid var(--tsi-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px; font-size:13px; color:var(--tsi-muted); }",
        "#cbi-tailscale-iface .table { width:100%; border-collapse:collapse; }",
        "#cbi-tailscale-iface .th { padding:0 0 12px; border-bottom:1px solid var(--tsi-border); font-size:16px; font-weight:600; color:var(--tsi-text); text-align:left; }",
        "#cbi-tailscale-iface .tr .td { padding:10px 8px; border-bottom:1px solid var(--tsi-border); font-size:13px; color:var(--tsi-text); }",
        "#cbi-tailscale-iface .tr:last-child .td { border-bottom:0; }",
        "#cbi-tailscale-iface .tr .td:first-child { width:180px; color:var(--tsi-muted); font-weight:600; }",
        "#cbi-tailscale-iface .tr .td:last-child { font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; }",
    ]
    iface_css_js = " +\n".join("\t\t\t" + repr(line + "\n") for line in iface_css)
    new_iface = (
        "\trender(data) {\n"
        "\t\tconst css = '' +\n"
        + iface_css_js
        + ";\n"
        "\t\tconst container = E('div', { class: 'ts-iface-card' });\n"
        "\t\tconst content = E('div', { id: 'cbi-tailscale-iface', class: 'cbi-map' }, [\n"
        "\t\t\tE('style', { 'data-ui-skin': 'tailscale-iface' }, [ css ]),\n"
        "\t\t\tE('div', { class: 'ts-iface-head' }, [\n"
        "\t\t\t\tE('h2', { class: 'content' }, _('Tailscale')),\n"
        "\t\t\t\tE('div', { class: 'cbi-map-descr' }, _('Tailscale is a cross-platform and easy to use virtual LAN.'))\n"
        "\t\t\t]),\n"
        "\t\t\tcontainer\n"
        "\t\t]);\n\n"
        "\t\tdom.content(container, this.renderContent(data));\n"
        "\t\tthis.pollData(container);\n\n"
        "\t\treturn content;\n"
        "\t},"
    )
    t = t.replace(old_iface, new_iface, 1)
    for must in ("#cbi-tailscale-iface", "'data-ui-skin': 'tailscale-iface'", "ts-iface-head", "renderContent", "pollData", "Network Interface Information"):
        if must not in t:
            raise SystemExit(f"tailscale interface.js missing {must}")
    iface_path.write_text(t, encoding="utf-8")
    print(f"OK    tailscale interface.js skinned ({iface_path})")

# --- 2) log.js ---
tl = log_path.read_text(encoding="utf-8")
if "'data-ui-skin': 'tailscale-log'" in tl and "#cbi-tailscale-log" in tl:
    print("SKIP  tailscale log.js: already skinned")
else:
    old_log = """\t\treturn E([], [
\t\t\tE('div', { id: 'content_syslog' }, [
\t\t\t\tE('div', { style: 'padding-bottom: 20px' }, [scrollDownButton]),
\t\t\t\tE('textarea', {
\t\t\t\t\tid: 'syslog',
\t\t\t\t\tstyle: 'font-size:12px',
\t\t\t\t\treadonly: 'readonly',
\t\t\t\t\twrap: 'off',
\t\t\t\t\trows: loglines.rows,
\t\t\t\t}, [ loglines.value ]),
\t\t\t\tE('div', { style: 'padding-bottom: 20px' }, [scrollUpButton])
\t\t\t])
\t\t]);"""
    if old_log not in tl:
        raise SystemExit("tailscale log.js: return E([], ...) anchor not found")
    log_css = [
        "#cbi-tailscale-log {",
        "	--tsl-accent: #5e72e4; --tsl-border: #e9ecef; --tsl-muted: #8898aa;",
        "	--tsl-text: #32325d; --tsl-card: #fff; --tsl-soft: #f7f9fc;",
        "}",
        "#cbi-tailscale-log.cbi-section, #cbi-tailscale-log .cbi-section { padding:0; border:0; background:none; box-shadow:none; margin:0; }",
        'body[theme="dark"] #cbi-tailscale-log { --tsl-border:#3a3a3d; --tsl-muted:#9aa2ad; --tsl-text:#d7dae0; --tsl-card:#232324; --tsl-soft:#2b2b2d; }',
        '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-tailscale-log { --tsl-border:#3a3a3d; --tsl-muted:#9aa2ad; --tsl-text:#d7dae0; --tsl-card:#232324; --tsl-soft:#2b2b2d; } }',
        "#cbi-tailscale-log .ts-log-card { background:var(--tsl-card); border:1px solid var(--tsl-border); border-radius:12px; box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px; }",
        "#cbi-tailscale-log .ts-log-actions { margin:0 0 12px; padding:0 !important; }",
        "#cbi-tailscale-log .ts-log-actions-bottom { margin:12px 0 0; padding:0 !important; }",
        "#cbi-tailscale-log .cbi-button { min-width:132px; padding:8px 18px; border-radius:8px; font-size:14px; }",
        "#cbi-tailscale-log #syslog { width:100%; box-sizing:border-box; padding:14px 16px; border:1px solid var(--tsl-border); border-radius:10px; background:var(--tsl-soft); color:var(--tsl-text); font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px !important; line-height:1.6; }",
    ]
    log_css_js = " +\n".join("\t\t\t" + repr(line + "\n") for line in log_css)
    new_log = (
        "\t\tconst css = '' +\n"
        + log_css_js
        + ";\n\n"
        "\t\treturn E('div', { id: 'cbi-tailscale-log', class: 'cbi-map' }, [\n"
        "\t\t\tE('style', { 'data-ui-skin': 'tailscale-log' }, [ css ]),\n"
        "\t\t\tE('div', { class: 'cbi-section' }, [\n"
        "\t\t\t\tE('div', { class: 'ts-log-card', id: 'content_syslog' }, [\n"
        "\t\t\t\t\tE('div', { class: 'ts-log-actions' }, [scrollDownButton]),\n"
        "\t\t\t\t\tE('textarea', {\n"
        "\t\t\t\t\t\tid: 'syslog',\n"
        "\t\t\t\t\t\tstyle: 'font-size:12px',\n"
        "\t\t\t\t\t\treadonly: 'readonly',\n"
        "\t\t\t\t\t\twrap: 'off',\n"
        "\t\t\t\t\t\trows: loglines.rows,\n"
        "\t\t\t\t\t}, [ loglines.value ]),\n"
        "\t\t\t\t\tE('div', { class: 'ts-log-actions ts-log-actions-bottom' }, [scrollUpButton])\n"
        "\t\t\t\t])\n"
        "\t\t\t])\n"
        "\t\t]);"
    )
    tl = tl.replace(old_log, new_log, 1)
    for must in ("#cbi-tailscale-log", "'data-ui-skin': 'tailscale-log'", "content_syslog", "scrollDownButton", "scrollUpButton", "syslog"):
        if must not in tl:
            raise SystemExit(f"tailscale log.js missing {must}")
    log_path.write_text(tl, encoding="utf-8")
    print(f"OK    tailscale log.js skinned ({log_path})")
