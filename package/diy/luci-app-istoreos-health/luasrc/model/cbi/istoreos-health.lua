local m, s, o

m = Map("istoreos-health", translate("Health Check"),
	translate("Daily health inspection (Tailscale / firewall / durable helper / DNS). Optional Telegram notify. Bot token is stored in /etc/config/istoreos-health (mode 600) and is never written to health logs."))

s = m:section(NamedSection, "notify", "notify", translate("Notification"))
s.anonymous = true

o = s:option(Flag, "enabled", translate("Enable notifications"))
o.default = "0"

o = s:option(ListValue, "when", translate("When to notify"))
o:value("fail", translate("On failure only"))
o:value("always", translate("Always (OK and FAIL)"))
o.default = "fail"

o = s:option(Flag, "telegram", translate("Telegram"))
o.default = "0"

o = s:option(Value, "tg_token", translate("Bot token"))
o.password = true
o.datatype = "string"
o:depends("telegram", "1")
o.placeholder = "123456:ABC-DEF..."
function o.write(self, section, value)
	if value and #value > 0 then
		Value.write(self, section, value)
	end
end

o = s:option(Value, "tg_chat_id", translate("Chat ID"))
o.datatype = "string"
o:depends("telegram", "1")
o.placeholder = "-100..."

local t = m:section(SimpleSection)
t.template = "istoreos-health/actions"

return m
