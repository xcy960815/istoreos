#!/bin/sh
# Keep luci-app-tailscale helper from recreating netifd network.tailscale (static IP)
# and ensure firewall.tszone binds device tailscale0 (no duplicate name=tailscale zones).
# Safe to run anytime; no-op when already correct.
# Shipped by pin-tailscale-prebuilt.sh durable overlay (docs/CUSTOM-TRIMMING.md §二十二).

KEEP=/etc/tailscale/tailscale_helper.keep
HELPER=/usr/sbin/tailscale_helper
MARKER="netifd skip: Tailscale owns addrs"
LOGTAG=tailscale-fixup

log() { logger -t "$LOGTAG" "$*"; echo "$*"; }

[ -f "$KEEP" ] || { log "missing $KEEP"; exit 1; }

need_helper=0
if ! grep -qF "$MARKER" "$HELPER" 2>/dev/null; then
	need_helper=1
fi
if grep -q "set network.tailscale.proto='static'" "$HELPER" 2>/dev/null; then
	need_helper=1
fi
if grep -q "set firewall.tszone.network='tailscale'" "$HELPER" 2>/dev/null; then
	need_helper=1
fi

if [ "$need_helper" = 1 ]; then
	cp -a "$KEEP" "$HELPER"
	chmod 755 "$HELPER"
	log "restored patched helper from $KEEP"
else
	log "helper already patched"
fi

# UCI: drop netifd-managed interface if present (causes address fight)
if uci -q get network.tailscale >/dev/null 2>&1; then
	uci -q delete network.tailscale
	uci commit network
	log "removed network.tailscale from netifd"
fi

fw_changed=0

# Remove duplicate zones named tailscale; keep only firewall.tszone
for sec in $(uci show firewall 2>/dev/null | sed -n "s/^\(firewall\.[^=]*\)\.name='tailscale'$/\1/p"); do
	case "$sec" in
		firewall.tszone) ;;
		*)
			uci -q delete "$sec"
			fw_changed=1
			log "removed duplicate zone $sec"
			;;
	esac
done

# UCI: zone must use device=tailscale0
if [ "$(uci -q get firewall.tszone.name)" = "tailscale" ]; then
	if uci -q get firewall.tszone.network >/dev/null 2>&1; then
		uci -q delete firewall.tszone.network
		fw_changed=1
	fi
	devs="$(uci -q get firewall.tszone.device 2>/dev/null)"
	case " $devs " in
		*" tailscale0 "*) ;;
		*)
			uci -q delete firewall.tszone.device 2>/dev/null
			uci add_list firewall.tszone.device='tailscale0'
			fw_changed=1
			;;
	esac
fi

if [ "$fw_changed" = 1 ]; then
	uci commit firewall
	log "fixed firewall.tszone / duplicate zones"
	/etc/init.d/firewall reload >/dev/null 2>&1 || true
fi

exit 0
