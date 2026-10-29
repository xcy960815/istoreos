#!/usr/bin/env bash
# Post-clone LuCI patches for asvow luci-app-tailscale (called by pin-tailscale-prebuilt.sh).
# 1) authKey → authkey (init/config option name)
# 2) NeedsLogin UI: inline AuthURL link (no cbi-button — Argon misaligns it), await AuthURL after login
# 3) zh_Hans 「授权登录」; waiting copy when AuthURL not ready yet
set -euo pipefail

luci=${1:?luci-app-tailscale package dir}
SETTING_JS="$luci/htdocs/luci-static/resources/view/tailscale/setting.js"
[ -f "$SETTING_JS" ] || { echo "::error::缺少 $SETTING_JS"; exit 1; }

if grep -q "form.Value, 'authKey'" "$SETTING_JS"; then
  tmp=$(mktemp)
  sed "s/form.Value, 'authKey'/form.Value, 'authkey'/" "$SETTING_JS" > "$tmp"
  mv "$tmp" "$SETTING_JS"
fi
grep -q "form.Value, 'authkey'" "$SETTING_JS" || { echo "::error::setting.js authkey 补丁失败"; exit 1; }
if grep -q "form.Value, 'authKey'" "$SETTING_JS"; then
  echo "::error::setting.js 仍含 authKey"
  exit 1
fi

python3 - "$SETTING_JS" <<'PY'
from pathlib import Path
import sys
import re

p = Path(sys.argv[1])
t = p.read_text()

# --- 1) getStatus: await AuthURL after triggering login (stock fires login and returns empty) ---
old_get = '''\tconst tailscaleRes = await fs.exec("/usr/sbin/tailscale", ["status", "--json"]);
\tconst tailscaleStatus = JSON.parse(tailscaleRes.stdout.replace(/("\\w+"):\\s*(\\d+)/g, '$1:"$2"'));
\tif (!tailscaleStatus.AuthURL && tailscaleStatus.BackendState === "NeedsLogin") {
\t\tfs.exec("/usr/sbin/tailscale", ["login"]);
\t}
\tstatus.backendState = tailscaleStatus.BackendState;
\tstatus.authURL = tailscaleStatus.AuthURL;'''

new_get = '''\tconst parseStatus = (stdout) => JSON.parse(stdout.replace(/("\\w+"):\\s*(\\d+)/g, '$1:"$2"'));
\tlet tailscaleRes = await fs.exec("/usr/sbin/tailscale", ["status", "--json"]);
\tlet tailscaleStatus = parseStatus(tailscaleRes.stdout);
\tif (!tailscaleStatus.AuthURL && tailscaleStatus.BackendState === "NeedsLogin") {
\t\tawait fs.exec("/usr/sbin/tailscale", ["login"]);
\t\tfor (let i = 0; i < 10 && !tailscaleStatus.AuthURL; i++) {
\t\t\tawait new Promise(r => setTimeout(r, 400));
\t\t\ttailscaleRes = await fs.exec("/usr/sbin/tailscale", ["status", "--json"]);
\t\t\ttry {
\t\t\t\ttailscaleStatus = parseStatus(tailscaleRes.stdout);
\t\t\t} catch (e) {
\t\t\t\tbreak;
\t\t\t}
\t\t\tif (tailscaleStatus.BackendState && tailscaleStatus.BackendState !== "NeedsLogin" && !tailscaleStatus.AuthURL)
\t\t\t\tbreak;
\t\t}
\t}
\tstatus.backendState = tailscaleStatus.BackendState;
\tstatus.authURL = tailscaleStatus.AuthURL;'''

# Also match already-awaited single-shot login without retry loop
old_get_await = '''\tconst tailscaleRes = await fs.exec("/usr/sbin/tailscale", ["status", "--json"]);
\tconst tailscaleStatus = JSON.parse(tailscaleRes.stdout.replace(/("\\w+"):\\s*(\\d+)/g, '$1:"$2"'));
\tif (!tailscaleStatus.AuthURL && tailscaleStatus.BackendState === "NeedsLogin") {
\t\tawait fs.exec("/usr/sbin/tailscale", ["login"]);
\t}
\tstatus.backendState = tailscaleStatus.BackendState;
\tstatus.authURL = tailscaleStatus.AuthURL;'''

if "parseStatus" in t and "for (let i = 0; i < 10" in t:
    print("setting.js getStatus AuthURL await already patched")
elif old_get in t:
    t = t.replace(old_get, new_get, 1)
    print("setting.js getStatus AuthURL await patched")
elif old_get_await in t:
    t = t.replace(old_get_await, new_get, 1)
    print("setting.js getStatus AuthURL await patched (from await-only)")
else:
    raise SystemExit("setting.js getStatus NeedsLogin block not found")

# --- 2) renderLogin: plain inline <a> (NOT cbi-button — floats/misaligns in Argon cbi-value) ---
# Accept stock, previous cbi-button patch, or already-new form.
stock_login = (
    "\tif (loginStatus === \"NeedsLogin\") {\n"
    "\t\trenderHTML = String.format('<a href=\"%s\" target=\"_blank\">%s</a>', authURL, _('Need to log in'));\n"
    "\t} else if (loginStatus === \"Running\") {"
)

# Previous patch (cbi-button) — whole NeedsLogin branch through Running
cbi_login_re = re.compile(
    r'\tif \(loginStatus === "NeedsLogin"\) \{\n'
    r'(?:\t\tif \(authURL\) \{\n'
    r'\t\t\trenderHTML = String\.format\(\'<a class="cbi-button cbi-button-apply"[^;]+;\n'
    r'\t\t\} else \{\n'
    r'\t\t\trenderHTML = String\.format\(\'<span style="color:orange">%s</span>\'[^;]+;\n'
    r'\t\t\}\n'
    r'|\t\trenderHTML = String\.format\(\'<a class="cbi-button cbi-button-apply"[^;]+;\n)'
    r'\t\} else if \(loginStatus === "Running"\) \{',
    re.M,
)

new_login = (
    "\tif (loginStatus === \"NeedsLogin\") {\n"
    "\t\tif (authURL) {\n"
    "\t\t\t/* plain <a> keeps horizontal alignment with cbi-value-title; cbi-button floats in Argon */\n"
    "\t\t\trenderHTML = String.format('<a href=\"%s\" target=\"_blank\" rel=\"noopener noreferrer\" style=\"color:#ff8c00;font-weight:600;text-decoration:underline;vertical-align:middle\">%s</a>', authURL, _('Need to log in'));\n"
    "\t\t} else {\n"
    "\t\t\trenderHTML = String.format('<span style=\"color:orange;vertical-align:middle\">%s</span>', _('Waiting for auth URL'));\n"
    "\t\t}\n"
    "\t} else if (loginStatus === \"Running\") {"
)

already_new = "Waiting for auth URL" in t and "noopener noreferrer" in t and "cbi-button-apply" not in t

if already_new:
    print("setting.js NeedsLogin UI already patched (inline link)")
elif stock_login in t:
    t = t.replace(stock_login, new_login, 1)
    print("setting.js NeedsLogin UI patched (from stock)")
elif cbi_login_re.search(t):
    t = cbi_login_re.sub(new_login, t, count=1)
    print("setting.js NeedsLogin UI patched (replaced cbi-button)")
elif "cbi-button-apply" in t and "Need to log in" in t:
    # Fallback: replace the whole NeedsLogin if-block more loosely
    loose = re.compile(
        r'\tif \(loginStatus === "NeedsLogin"\) \{.*?\t\} else if \(loginStatus === "Running"\) \{',
        re.S,
    )
    m = loose.search(t)
    if not m:
        raise SystemExit("setting.js NeedsLogin block not found for UI patch (cbi fallback)")
    t = t[:m.start()] + new_login + t[m.end():]
    print("setting.js NeedsLogin UI patched (loose cbi replace)")
else:
    raise SystemExit("setting.js NeedsLogin block not found for UI patch")

# --- 3) renderWidget: keep value cell vertically centered with the title ---
old_widget = (
    "\t\to.renderWidget = function(section_id, option_id) {\n"
    "\t\t\treturn E('div', { 'id': 'login_status_div' }, _('Collecting data ...'));\n"
    "\t\t};"
)
new_widget = (
    "\t\to.renderWidget = function(section_id, option_id) {\n"
    "\t\t\treturn E('div', {\n"
    "\t\t\t\t'id': 'login_status_div',\n"
    "\t\t\t\t'style': 'display:flex;align-items:center;min-height:2.2em;line-height:normal'\n"
    "\t\t\t}, _('Collecting data ...'));\n"
    "\t\t};"
)

if "display:flex;align-items:center;min-height:2.2em" in t:
    print("setting.js login_status_div align already patched")
elif old_widget in t:
    t = t.replace(old_widget, new_widget, 1)
    print("setting.js login_status_div align patched")
else:
    raise SystemExit("setting.js renderWidget login_status_div not found")

if "cbi-button-apply" in t:
    raise SystemExit("setting.js still contains cbi-button-apply (alignment regress)")

p.write_text(t)
print("setting.js write ok")
PY

PO_ZH="$luci/po/zh_Hans/tailscale.po"
if [ -f "$PO_ZH" ]; then
  python3 - "$PO_ZH" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
lines = text.splitlines(keepends=True)
out = []
i = 0
changed_login = False
while i < len(lines):
    out.append(lines[i])
    if lines[i].rstrip("\n") == 'msgid "Need to log in"':
        i += 1
        if i < len(lines) and lines[i].startswith("msgstr "):
            out.append('msgstr "授权登录"\n')
            changed_login = True
            i += 1
            continue
    i += 1
text = "".join(out)
if 'msgid "Waiting for auth URL"' not in text:
    text += '\nmsgid "Waiting for auth URL"\nmsgstr "正在获取授权链接…"\n'
    print("zh_Hans added Waiting for auth URL")
else:
    # ensure translation
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].rstrip("\n") == 'msgid "Waiting for auth URL"':
            i += 1
            if i < len(lines) and lines[i].startswith("msgstr "):
                out.append('msgstr "正在获取授权链接…"\n')
                i += 1
                continue
        i += 1
    text = "".join(out)
    print("zh_Hans Waiting for auth URL msgstr refreshed")
p.write_text(text)
if not changed_login and 'msgstr "授权登录"' not in p.read_text():
    raise SystemExit("zh_Hans 授权登录 patch failed")
print("zh_Hans Need to log in → 授权登录")
PY
fi

# Sanity: patched markers
grep -q 'Waiting for auth URL' "$SETTING_JS" || { echo "::error::setting.js 缺少 Waiting for auth URL 分支"; exit 1; }
grep -q 'noopener noreferrer' "$SETTING_JS" || { echo "::error::setting.js 缺少 AuthURL 链接"; exit 1; }
grep -q 'parseStatus' "$SETTING_JS" || { echo "::error::setting.js 缺少 AuthURL await"; exit 1; }
grep -q 'cbi-button-apply' "$SETTING_JS" && { echo "::error::setting.js 仍含 cbi-button-apply"; exit 1; }
echo "patch-luci-setting.sh OK"
