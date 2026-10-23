local m, s, o

m = Map("ota", translate("OTA Configuration"),
	translate("This build upgrades from GitHub Releases of the trimmed fork (not official koolcenter images)."))

s = m:section(NamedSection, "network", "global", translate("Network"))
s.anonymous = true
o = s:option(Flag, "ipv4", translate("IPv4 only"), translate("Use IPv4 network for OTA operations"))

s = m:section(NamedSection, "github", "github", translate("GitHub Release source"))
s.anonymous = true
o = s:option(Value, "owner", translate("Owner"))
o.datatype = "string"
o.default = "xcy960815"
o = s:option(Value, "repo", translate("Repository"))
o.datatype = "string"
o.default = "istoreos"
o = s:option(Value, "asset_suffix", translate("Asset name suffix"),
	translate("Default: squashfs-combined-efi.img.gz (GPT/EFI). Use squashfs-combined.img.gz for legacy MBR if needed."))
o.datatype = "string"
o.placeholder = "squashfs-combined-efi.img.gz"

return m
