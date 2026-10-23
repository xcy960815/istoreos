local m, s, o

m = Map("istoreos-health", translate("Health Check"),
	translate("Daily health inspection (Tailscale / firewall / durable helper / DNS). Optional Telegram and email notify. Secrets are stored in /etc/config/istoreos-health (mode 600) and are never written to health logs."))

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

o = s:option(Flag, "email", translate("Email (SMTP)"))
o.default = "0"

o = s:option(Value, "smtp_host", translate("SMTP host"))
o.datatype = "host"
o:depends("email", "1")

o = s:option(Value, "smtp_port", translate("SMTP port"))
o.datatype = "port"
o.default = "465"
o:depends("email", "1")

o = s:option(ListValue, "smtp_tls", translate("TLS mode"))
o:value("smtps", translate("SMTPS (implicit TLS, typically 465)"))
o:value("starttls", translate("STARTTLS (typically 587)"))
o:value("off", translate("No TLS (not recommended)"))
o.default = "smtps"
o:depends("email", "1")

o = s:option(Value, "smtp_user", translate("SMTP username"))
o.datatype = "string"
o:depends("email", "1")

o = s:option(Value, "smtp_pass", translate("SMTP password"))
o.password = true
o.datatype = "string"
o:depends("email", "1")
function o.write(self, section, value)
	if value and #value > 0 then
		Value.write(self, section, value)
	end
end

o = s:option(Value, "smtp_from", translate("From address"))
o.datatype = "string"
o:depends("email", "1")

o = s:option(Value, "smtp_to", translate("To address"))
o.datatype = "string"
o:depends("email", "1")

local t = m:section(SimpleSection)
t.template = "istoreos-health/actions"

return m
