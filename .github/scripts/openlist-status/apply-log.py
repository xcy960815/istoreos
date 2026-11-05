#!/usr/bin/env python3
from pathlib import Path
import sys

p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8")
if "data-ui-skin" in t and "#cbi-openlist-log" in t:
    print("SKIP  openlist log.js: already skinned")
    raise SystemExit(0)

old_css = """\t\tvar css = '\t\t\t\t\t\\
\t\t\t#log_textarea {\t\t\t\t\\
\t\t\t\tpadding: 10px;\t\t\t\\
\t\t\t\ttext-align: left;\t\t\\
\t\t\t}\t\t\t\t\t\\
\t\t\t#log_textarea pre {\t\t\t\\
\t\t\t\tpadding: .5rem;\t\t\t\\
\t\t\t\tword-break: break-all;\t\t\\
\t\t\t\tmargin: 0;\t\t\t\\
\t\t\t}\t\t\t\t\t\\
\t\t\t.description {\t\t\t\t\\
\t\t\t\tbackground-color: #33ccff;\t\\
\t\t\t}';"""

old_ret = """\t\treturn E([
\t\t\tE('style', [ css ]),
\t\t\tE('div', {'class': 'cbi-map'}, [
\t\t\t\tE('div', {'class': 'cbi-section'}, [
\t\t\t\t\tlog_textarea,
\t\t\t\t\tE('div', {'style': 'text-align:right'},
\t\t\t\t\tE('small', {}, _('Refresh every %s seconds.').format(L.env.pollinterval))
\t\t\t\t\t)
\t\t\t\t])
\t\t\t])
\t\t]);"""

if old_css not in t or old_ret not in t:
    raise SystemExit("openlist log.js: expected upstream anchors not found")

css_lines = [
    "#cbi-openlist-log {",
    "	--ol-border: #e9ecef; --ol-muted: #8898aa; --ol-text: #32325d; --ol-card: #fff; --ol-soft: #f7f9fc;",
    "}",
    'body[theme="dark"] #cbi-openlist-log { --ol-border:#3a3a3d; --ol-muted:#9aa2ad; --ol-text:#d7dae0; --ol-card:#232324; --ol-soft:#2b2b2d; }',
    '@media (prefers-color-scheme: dark) { body[theme="normal"] #cbi-openlist-log { --ol-border:#3a3a3d; --ol-muted:#9aa2ad; --ol-text:#d7dae0; --ol-card:#232324; --ol-soft:#2b2b2d; } }',
    "#cbi-openlist-log .cbi-section {",
    "	background:var(--ol-card); border:1px solid var(--ol-border); border-radius:12px;",
    "	box-shadow:0 2px 12px rgba(50,50,93,.06); padding:20px 22px; margin:0 0 16px;",
    "}",
    "#cbi-openlist-log #log_textarea { padding:0; text-align:left; }",
    "#cbi-openlist-log #log_textarea pre {",
    "	margin:0; padding:14px 16px; border:1px solid var(--ol-border); border-radius:10px;",
    "	background:var(--ol-soft); color:var(--ol-text);",
    "	font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:12px; line-height:1.6;",
    "	white-space:pre-wrap; word-break:break-word; max-height:70vh; overflow:auto;",
    "}",
    "#cbi-openlist-log .ol-log-foot { margin-top:10px; text-align:right; font-size:12px; color:var(--ol-muted); }",
]
new_css = "\t\tvar css = '' +\n" + " +\n".join("\t\t\t" + repr(line + "\n") for line in css_lines) + ";"

new_ret = """\t\treturn E('div', { 'id': 'cbi-openlist-log', 'class': 'cbi-map' }, [
\t\t\tE('style', { 'data-ui-skin': 'openlist-log' }, [ css ]),
\t\t\tE('div', { 'class': 'cbi-section' }, [
\t\t\t\tlog_textarea,
\t\t\t\tE('div', { 'class': 'ol-log-foot' },
\t\t\t\t\tE('small', {}, _('Refresh every %s seconds.').format(L.env.pollinterval))
\t\t\t\t)
\t\t\t])
\t\t]);"""

t = t.replace(old_css, new_css, 1).replace(old_ret, new_ret, 1)

for must in ("#cbi-openlist-log", "data-ui-skin", "log_textarea", "/var/run/openlist/log/openlist.log", "NotFoundError"):
    if must not in t:
        raise SystemExit(f"openlist log.js missing {must}")

p.write_text(t, encoding="utf-8")
print(f"OK    openlist log.js skinned ({p})")
