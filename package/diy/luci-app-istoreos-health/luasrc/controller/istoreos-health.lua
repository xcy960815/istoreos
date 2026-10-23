--[[
LuCI controller — 服务 → 健康巡检
]]--

module("luci.controller.istoreos-health", package.seeall)

function index()
	if not nixio.fs.access("/etc/config/istoreos-health") then
		return
	end
	entry({"admin", "services", "istoreos-health"}, cbi("istoreos-health"), _("Health Check"), 92).dependent = true
	entry({"admin", "services", "istoreos-health", "test_telegram"}, post("action_test_telegram")).leaf = true
	entry({"admin", "services", "istoreos-health", "run_health"}, post("action_run_health")).leaf = true
end

local function run_notify(cmd)
	local fs = require "nixio.fs"
	local r = os.execute(cmd .. " >/tmp/istoreos-notify-luci.out 2>/tmp/istoreos-notify-luci.err")
	local o = fs.readfile("/tmp/istoreos-notify-luci.out") or ""
	local e = fs.readfile("/tmp/istoreos-notify-luci.err") or ""
	fs.unlink("/tmp/istoreos-notify-luci.out")
	fs.unlink("/tmp/istoreos-notify-luci.err")
	o = o:gsub("bot%d+:%S+", "bot***:***")
	e = e:gsub("bot%d+:%S+", "bot***:***")
	local code = 1
	if r == 0 or r == true then
		code = 0
	elseif type(r) == "number" then
		code = math.floor(r / 256)
	end
	return code, o, e
end

function action_test_telegram()
	local code, o, e = run_notify("/usr/sbin/istoreos-health-notify test-telegram")
	luci.http.prepare_content("application/json")
	luci.http.write_json({ code = code, msg = (o ~= "" and o or e) })
end

function action_run_health()
	local fs = require "nixio.fs"
	local r = os.execute("/usr/sbin/istoreos-health >/tmp/istoreos-health-luci.out 2>/tmp/istoreos-health-luci.err")
	local o = fs.readfile("/tmp/istoreos-health-luci.out") or ""
	local e = fs.readfile("/tmp/istoreos-health-luci.err") or ""
	local report = fs.readfile("/tmp/istoreos-health.report") or o
	fs.unlink("/tmp/istoreos-health-luci.out")
	fs.unlink("/tmp/istoreos-health-luci.err")
	local code = 1
	if r == 0 or r == true then
		code = 0
	elseif type(r) == "number" then
		code = math.floor(r / 256)
	end
	luci.http.prepare_content("application/json")
	luci.http.write_json({ code = code, msg = report, err = e })
end
