#!/usr/bin/env bash
# Keep tailscale0's 100.x address. asvow start always ran `tailscaled --cleanup`,
# and hotplug called start on every ifup/ifupdate. Cleanup against a live
# daemon deletes the address (log: "stale Tailscale address(es) ... during cleanup")
# while procd leaves the old pid running, so the address does not come back.
# Same change verified on the J4125 overlay 2026-11-04. See docs/CUSTOM-TRIMMING.md §二十二.
set -euo pipefail

luci=${1:?luci-app-tailscale package dir}
INIT="$luci/root/etc/init.d/tailscale"
HOTPLUG="$luci/root/etc/hotplug.d/iface/40-tailscale"
[ -f "$INIT" ] || { echo "::error::缺少 $INIT"; exit 1; }
[ -f "$HOTPLUG" ] || { echo "::error::缺少 $HOTPLUG"; exit 1; }

python3 - "$INIT" "$HOTPLUG" <<'PY'
from pathlib import Path
import sys

init_path, hotplug_path = map(Path, sys.argv[1:])
init_marker = "running --cleanup against a live instance strips tailscale0."
hotplug_marker = "do not re-run start (and its --cleanup) while tailscaled is up."

init = init_path.read_text()
old_init = (
    '\tstate_file="$config_path/tailscaled.state"\n'
    '\t\n'
    '\t/usr/sbin/tailscaled --cleanup\n'
    '\n'
    '\tprocd_open_instance\n'
)
new_init = (
    '\tstate_file="$config_path/tailscaled.state"\n'
    '\t\n'
    '\t# FIXED: only clean up when tailscaled is not already running;\n'
    '\t# running --cleanup against a live instance strips tailscale0.\n'
    '\tpidof tailscaled >/dev/null 2>&1 || /usr/sbin/tailscaled --cleanup\n'
    '\n'
    '\tprocd_open_instance\n'
)
if init_marker in init:
    print("tailscale init cleanup guard already patched")
elif old_init in init:
    init = init.replace(old_init, new_init, 1)
    init_path.write_text(init)
    print("tailscale init cleanup guard patched")
else:
    raise SystemExit("::error::tailscale init 找不到 start 里的 --cleanup 锚点，asvow 布局变了")

bare = init.count("\t/usr/sbin/tailscaled --cleanup\n")
if bare != 1:
    raise SystemExit(f"::error::tailscale init 裸 --cleanup 应只留 stop 一处，实际 {bare}")
if init_marker not in init_path.read_text():
    raise SystemExit("::error::tailscale init 补丁后缺少标记")

hotplug = hotplug_path.read_text()
old_hotplug = "/etc/init.d/tailscale start > /tmp/tailscale.log 2>&1 &\n"
new_hotplug = (
    "# FIXED: do not re-run start (and its --cleanup) while tailscaled is up.\n"
    "if ! pidof tailscaled >/dev/null 2>&1; then\n"
    "\t/etc/init.d/tailscale start > /tmp/tailscale.log 2>&1 &\n"
    "fi\n"
)
if hotplug_marker in hotplug:
    print("tailscale hotplug already patched")
elif hotplug.endswith(old_hotplug) and hotplug.count(old_hotplug) == 1:
    hotplug_path.write_text(hotplug[: -len(old_hotplug)] + new_hotplug)
    print("tailscale hotplug patched")
else:
    raise SystemExit("::error::40-tailscale 找不到无条件 start 锚点，asvow 布局变了")
if hotplug_marker not in hotplug_path.read_text():
    raise SystemExit("::error::40-tailscale 补丁后缺少标记")
PY
