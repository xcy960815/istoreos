#!/usr/bin/env python3
"""
生成 LuCI 页面样式重构的本地自包含 HTML 预览文件。
执行方式: python3 docs/preview-ui/generate.py
产物目录: docs/preview-ui/
"""

from pathlib import Path
import re

cur_dir = Path(__file__).resolve().parent
repo_root = cur_dir.parent.parent

def extract_css_from_py(file_path):
    p = repo_root / file_path
    if not p.exists():
        return ""
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"css_lines\s*=\s*\[(.*?)\]\ncss_js", txt, re.S)
    if not m:
        return ""
    lines = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith('"') and line.endswith('",'):
            lines.append(line[1:-2])
        elif line.startswith("'") and line.endswith("',"):
            lines.append(line[1:-2])
    return "\n".join(lines)

def extract_css_from_htm(file_path):
    p = repo_root / file_path
    if not p.exists():
        return ""
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"<style[^>]*>(.*?)</style>", txt, re.S)
    return m.group(1).strip() if m else ""

ttyd_css = extract_css_from_py(".github/scripts/ttyd-ui/apply-ttyd.py")
pw_css = extract_css_from_py(".github/scripts/luci-mod-system-ui/apply-password.py")
proc_css = extract_css_from_py(".github/scripts/status-logs-ui/apply-processes.py")
linkease_css = extract_css_from_htm(".github/scripts/openlist-status/linkease_status.htm")
sys_css = extract_css_from_py(".github/scripts/luci-mod-system-ui/apply-system.py")
sshkeys_css = extract_css_from_py(".github/scripts/luci-mod-system-ui/apply-sshkeys.py")
forwards_css = extract_css_from_py(".github/scripts/firewall-ui/apply-forwards.py")
dhcp_css = extract_css_from_py(".github/scripts/luci-mod-system-ui/apply-dhcp.py")

# 1. 终端预览
ttyd_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>系统终端 - UI 预览</title>
<style>
body {{ background:#f4f6fb; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:24px; }}
body[theme="dark"] {{ background:#181819; color:#d7dae0; }}
.cbi-map {{ max-width:1080px; margin:0 auto; }}
{ttyd_css}
</style></head>
<body>
<div id="cbi-ttyd" class="cbi-map">
	<div class="ttyd-head">
		<div class="ttyd-head-left">
			<h2 class="ttyd-title">终端</h2>
			<div class="cbi-map-descr">通过 Web 终端访问系统命令行。 <span class="ttyd-port-badge">端口: 7681</span></div>
		</div>
		<div class="ttyd-head-right">
			<a class="ttyd-open-btn" href="#" target="_blank">在新标签页打开 <span class="ttyd-external-icon">↗</span></a>
		</div>
	</div>
	<div class="ttyd-window">
		<div class="ttyd-window-bar">
			<div class="ttyd-dots">
				<span class="ttyd-dot ttyd-dot-red"></span>
				<span class="ttyd-dot ttyd-dot-yellow"></span>
				<span class="ttyd-dot ttyd-dot-green"></span>
			</div>
			<div class="ttyd-window-title">root@iStoreOS ~ ttyd</div>
		</div>
		<div style="height:420px; background:#000; color:#27c93f; font-family:monospace; padding:16px; font-size:13px; line-height:1.5;">
			root@iStoreOS:~# uname -a<br>
			Linux iStoreOS 6.6.54 #0 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux<br>
			root@iStoreOS:~# uptime<br>
			 11:15:30 up 12 days,  3:24,  load average: 0.08, 0.04, 0.01<br>
			root@iStoreOS:~# _
		</div>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-ttyd.html").write_text(ttyd_html, encoding="utf-8")
(cur_dir / "preview-ttyd-dark.html").write_text(ttyd_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 2. 密码修改预览
pw_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>密码修改 - UI 预览</title>
<style>
body {{ background:#f4f6fb; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:24px; }}
body[theme="dark"] {{ background:#181819; color:#d7dae0; }}
.cbi-map {{ max-width:980px; margin:0 auto; }}
{pw_css}
</style></head>
<body>
<div id="cbi-password" class="cbi-map">
	<div class="password-head">
		<div class="password-head-title"><h2>路由器密码</h2></div>
		<div class="password-head-descr"><div class="cbi-map-descr">修改访问设备的管理员密码</div></div>
	</div>
	<div class="cbi-section">
		<div class="cbi-section-node">
			<div class="cbi-value">
				<label class="cbi-value-title">密码</label>
				<div class="cbi-value-field">
					<input type="password" class="cbi-input-text" value="Admin@2026">
					<div class="cbi-value-description">密码强度: <span style="color:green">强</span></div>
				</div>
			</div>
			<div class="cbi-value">
				<label class="cbi-value-title">确认密码</label>
				<div class="cbi-value-field">
					<input type="password" class="cbi-input-text" value="Admin@2026">
				</div>
			</div>
			<div class="cbi-page-actions">
				<button class="cbi-button-save">保存</button>
			</div>
		</div>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-password.html").write_text(pw_html, encoding="utf-8")
(cur_dir / "preview-password-dark.html").write_text(pw_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 3. 系统进程预览
proc_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>系统进程 - UI 预览</title>
<style>
body {{ background:#f4f6fb; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:24px; }}
body[theme="dark"] {{ background:#181819; color:#d7dae0; }}
.cbi-map {{ max-width:1080px; margin:0 auto; }}
{proc_css}
</style></head>
<body>
<div id="cbi-processes" class="cbi-map">
	<div class="proc-head">
		<div class="proc-head-left">
			<h2 class="proc-title">系统进程</h2>
			<div class="cbi-map-descr">实时查看与管理系统运行中的进程。</div>
		</div>
		<div class="proc-head-right">
			<input type="text" class="proc-filter" placeholder="搜索进程名 / 命令行 / PID..." value="">
			<span class="proc-count-pill">活动进程: 3</span>
		</div>
	</div>
	<div class="cbi-section">
		<table class="table proc-table">
			<thead>
				<tr class="tr table-titles">
					<th class="th">PID</th>
					<th class="th">用户</th>
					<th class="th">命令行</th>
					<th class="th">CPU 使用率</th>
					<th class="th">内存使用率</th>
					<th class="th">操作</th>
				</tr>
			</thead>
			<tbody>
				<tr class="tr">
					<td class="td"><span class="proc-pid-badge">1</span></td>
					<td class="td">root</td>
					<td class="td"><span class="proc-cmd-text">/sbin/procd</span></td>
					<td class="td"><span class="proc-stat-badge">0.1%</span></td>
					<td class="td"><span class="proc-stat-badge">0.4%</span></td>
					<td class="td"><div class="proc-actions"><button class="proc-btn proc-btn-hup">挂起 (HUP)</button><button class="proc-btn proc-btn-term">终止 (TERM)</button><button class="proc-btn proc-btn-kill">强杀 (KILL)</button></div></td>
				</tr>
				<tr class="tr">
					<td class="td"><span class="proc-pid-badge">2410</span></td>
					<td class="td">root</td>
					<td class="td"><span class="proc-cmd-text">/usr/sbin/tailscaled --state=/etc/tailscale/tailscaled.state</span></td>
					<td class="td"><span class="proc-stat-badge">0.3%</span></td>
					<td class="td"><span class="proc-stat-badge">1.2%</span></td>
					<td class="td"><div class="proc-actions"><button class="proc-btn proc-btn-hup">挂起 (HUP)</button><button class="proc-btn proc-btn-term">终止 (TERM)</button><button class="proc-btn proc-btn-kill">强杀 (KILL)</button></div></td>
				</tr>
				<tr class="tr">
					<td class="td"><span class="proc-pid-badge">3125</span></td>
					<td class="td">root</td>
					<td class="td"><span class="proc-cmd-text">/usr/bin/ddns-go -f 10 -c /etc/ddns-go/ddns_go.yaml</span></td>
					<td class="td"><span class="proc-stat-badge">0.0%</span></td>
					<td class="td"><span class="proc-stat-badge">0.8%</span></td>
					<td class="td"><div class="proc-actions"><button class="proc-btn proc-btn-hup">挂起 (HUP)</button><button class="proc-btn proc-btn-term">终止 (TERM)</button><button class="proc-btn proc-btn-kill">强杀 (KILL)</button></div></td>
				</tr>
			</tbody>
		</table>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-processes.html").write_text(proc_html, encoding="utf-8")
(cur_dir / "preview-processes-dark.html").write_text(proc_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 4. 易有云文件管理器预览
linkease_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>易有云文件管理器 - UI 预览</title>
<style>
body {{ background:#f4f6fb; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:24px; }}
body[theme="dark"] {{ background:#181819; color:#d7dae0; }}
.cbi-map {{ max-width:980px; margin:0 auto; }}
{linkease_css}
</style></head>
<body>
<div id="cbi-linkease" class="cbi-map">
	<div class="linkease-head">
		<div class="linkease-head-left">
			<h2>易有云文件管理器</h2>
		</div>
		<div class="linkease-head-right">
			<div class="cbi-map-descr" title="易有云是一个微型家庭私有数据服务中心，主要用于文件的集中存放、读取、备份及日常管理。释放用户终端设备空间，实现个人、家庭文件长久留存；支持家庭相册、视频文件随时随地多终端查看、播放，满足家庭文件的日常管理。">
				微型家庭私有数据服务中心，支持多终端集中存储与文件管理。
			</div>
		</div>
	</div>

	<div id="cbi-linkease-status" class="cbi-section">
		<div class="linkease-card">
			<div class="linkease-row">
				<div class="linkease-label">易有云服务状态</div>
				<div class="linkease-actions">
					<span class="linkease-pill linkease-pill-ok"><span class="linkease-dot"></span>易有云服务已启动</span>
					<input class="cbi-button linkease-btn linkease-btn-primary" type="button" value="点击打开易有云">
					<input class="cbi-button linkease-btn linkease-btn-secondary" type="button" value="本地文件管理">
				</div>
			</div>
		</div>
	</div>

	<div class="cbi-section">
		<div class="cbi-section-node">
			<legend>全局设置</legend>
			<div class="cbi-value">
				<label class="cbi-value-title">启用</label>
				<div class="cbi-value-field">
					<input type="checkbox" class="cbi-input-checkbox" checked>
				</div>
			</div>
			<div class="cbi-value">
				<label class="cbi-value-title">端口</label>
				<div class="cbi-value-field">
					<input type="text" class="cbi-input-text" value="8897">
				</div>
			</div>
			<div class="cbi-value">
				<label class="cbi-value-title">公网访问</label>
				<div class="cbi-value-field">
					<input type="checkbox" class="cbi-input-checkbox">
					<div class="cbi-value-description">允许公网 IP 访问，可能会导致不够安全。</div>
				</div>
			</div>
		</div>

		<!-- 整合进卡片底部的操作栏：彻底消除下方巨大空白与悬空 -->
		<div class="cbi-page-actions">
			<button class="cbi-button cbi-button-reset">复位</button>
			<button class="cbi-button cbi-button-action">保存</button>
			<button class="cbi-button cbi-button-apply">保存并应用</button>
		</div>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-linkease.html").write_text(linkease_html, encoding="utf-8")
(cur_dir / "preview-linkease-dark.html").write_text(linkease_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 5. 系统属性预览 (系统 ➔ 系统属性)
sys_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>系统属性 - UI 预览</title>
<style>
body {{ background:#f4f6fb; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:24px; }}
body[theme="dark"] {{ background:#181819; color:#d7dae0; }}
.cbi-map {{ max-width:980px; margin:0 auto; }}
{sys_css}
</style></head>
<body>
<div id="cbi-system" class="cbi-map">
	<div class="system-head">
		<div class="system-head-left">
			<h2>系统属性</h2>
		</div>
		<div class="system-head-right">
			<div class="cbi-map-descr">配置设备基础参数、主机名、本地时区与时间同步服务。</div>
		</div>
	</div>

	<ul class="cbi-tabmenu">
		<li class="cbi-tab"><a href="#">常规设置</a></li>
		<li><a href="#">日志记录</a></li>
		<li><a href="#">时间同步</a></li>
		<li><a href="#">语言和界面</a></li>
	</ul>

	<div class="cbi-section">
		<div class="cbi-section-node">
			<div class="cbi-value">
				<label class="cbi-value-title">本地时间</label>
				<div class="cbi-value-field">
					<div class="systime-widget">
						<div class="systime-display">
							<span class="systime-icon">🕒</span>
							<input id="localtime" class="systime-input" readonly value="2026-11-17 13:48:22">
							<span class="systime-live-pill"><span class="systime-live-dot"></span>Live</span>
						</div>
						<div class="systime-actions">
							<button class="cbi-button systime-btn systime-btn-sync">与浏览器同步</button>
							<button class="cbi-button systime-btn systime-btn-ntp">与 NTP 同步</button>
						</div>
					</div>
					<div class="cbi-value-description">当前设备系统内核时钟，随 NTP 定时校验同步。</div>
				</div>
			</div>
			<div class="cbi-value">
				<label class="cbi-value-title">主机名</label>
				<div class="cbi-value-field">
					<input type="text" class="cbi-input-text" value="iStoreOS">
					<div class="cbi-value-description">网络上标识此路由器的计算机名称。</div>
				</div>
			</div>
			<div class="cbi-value">
				<label class="cbi-value-title">时区</label>
				<div class="cbi-value-field">
					<select class="cbi-input-select">
						<option selected>Asia/Shanghai (CST, +0800)</option>
						<option>UTC</option>
					</select>
				</div>
			</div>
		</div>

		<div class="cbi-page-actions">
			<button class="cbi-button cbi-button-reset">复位</button>
			<button class="cbi-button cbi-button-action">保存</button>
			<button class="cbi-button cbi-button-apply">保存并应用</button>
		</div>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-system.html").write_text(sys_html, encoding="utf-8")
(cur_dir / "preview-system-dark.html").write_text(sys_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 6. SSH 密钥预览 (系统 ➔ 管理权 ➔ SSH-Keys)
sshkeys_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>SSH 密钥 - UI 预览</title>
<style>
body {{ background:#f4f6fb; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:24px; }}
body[theme="dark"] {{ background:#181819; color:#d7dae0; }}
.cbi-map {{ max-width:980px; margin:0 auto; }}
{sshkeys_css}
</style></head>
<body>
<div id="cbi-sshkeys" class="cbi-map">
	<div class="sshkeys-head">
		<div class="sshkeys-head-left">
			<h2>SSH 密钥管理</h2>
		</div>
		<div class="sshkeys-head-right">
			<div class="cbi-map-descr">公钥允许免密码安全登录 SSH。粘贴公钥字符串或直接将 .pub 文件拖入下方输入区域。</div>
		</div>
	</div>

	<div class="cbi-section">
		<div class="cbi-section-node">
			<div class="cbi-dynlist">
				<div class="add-item">
					<input class="cbi-input-text" type="text" placeholder="粘贴或拖拽 SSH 公钥文件…">
					<button class="cbi-button">添加密钥</button>
				</div>
				<div class="item sshkey-item">
					<div class="sshkey-main">
						<div class="sshkey-title-row">
							<span class="sshkey-algo-badge">Ed25519 Curve25519</span>
							<strong class="sshkey-comment">opera@MacBook-Pro.local</strong>
						</div>
						<div class="sshkey-details">
							<code class="sshkey-fprint">AAAAC3NzaC1lZDI1NTE5AAAAIH...a8wL2J1qP</code>
						</div>
					</div>
					<button class="cbi-button sshkey-del-btn" title="删除密钥">🗑</button>
				</div>
				<div class="item sshkey-item">
					<div class="sshkey-main">
						<div class="sshkey-title-row">
							<span class="sshkey-algo-badge">RSA 4096 Bit</span>
							<strong class="sshkey-comment">ci-deploy-runner@github-actions</strong>
						</div>
						<div class="sshkey-details">
							<code class="sshkey-fprint">AAAAB3NzaC1yc2EAAAADAQABAA...Z9mU1t0P</code>
							<span class="sshkey-options">选项: <code>no-port-forwarding</code></span>
						</div>
					</div>
					<button class="cbi-button sshkey-del-btn" title="删除密钥">🗑</button>
				</div>
			</div>
		</div>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-sshkeys.html").write_text(sshkeys_html, encoding="utf-8")
(cur_dir / "preview-sshkeys-dark.html").write_text(sshkeys_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 7. 防火墙端口转发预览 (网络 ➔ 防火墙 ➔ 端口转发)
forwards_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>端口转发 - UI 预览</title>
<style>
body {{ background:#f4f6fb; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:24px; }}
body[theme="dark"] {{ background:#181819; color:#d7dae0; }}
.cbi-map {{ max-width:1080px; margin:0 auto; }}
{forwards_css}
</style></head>
<body>
<div id="cbi-firewall-forwards" class="cbi-map">
	<div class="forwards-head">
		<div class="forwards-head-left">
			<h2>防火墙 - 端口转发</h2>
		</div>
		<div class="forwards-head-right">
			<div class="cbi-map-descr">端口转发允许互联网远程计算机访问私有局域网内的指定服务或设备 (DNAT)。</div>
		</div>
	</div>

	<div class="cbi-section">
		<table class="cbi-section-table">
			<thead>
				<tr>
					<th>名称</th>
					<th>匹配条件 (协议 / 来源)</th>
					<th>转发目标 (内部 IP : 端口)</th>
					<th style="text-align:right">操作</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><strong>WebDAV 外网访问</strong></td>
					<td>
						<span class="zonebadge" style="background:#f5365c;color:#fff">WAN</span>
						协议 <var>TCP</var>，端口 <var>8080</var>
					</td>
					<td>
						➔ <span class="zonebadge" style="background:#2dce89;color:#fff">LAN</span>
						IP <var>192.168.1.1</var>，端口 <var>80</var>
					</td>
					<td style="text-align:right">
						<button class="cbi-button cbi-button-action" style="padding:4px 12px;border-radius:6px;font-size:12px;cursor:pointer">修改</button>
						<button class="cbi-button" style="padding:4px 12px;border-radius:6px;font-size:12px;background:rgba(245,54,92,.08);color:#f5365c;border:1px solid rgba(245,54,92,.2);cursor:pointer">删除</button>
					</td>
				</tr>
				<tr>
					<td><strong>NAS 控制台</strong></td>
					<td>
						<span class="zonebadge" style="background:#f5365c;color:#fff">WAN</span>
						协议 <var>TCP</var>，端口 <var>5001</var>
					</td>
					<td>
						➔ <span class="zonebadge" style="background:#2dce89;color:#fff">LAN</span>
						IP <var>192.168.1.100</var>，端口 <var>5001</var>
					</td>
					<td style="text-align:right">
						<button class="cbi-button cbi-button-action" style="padding:4px 12px;border-radius:6px;font-size:12px;cursor:pointer">修改</button>
						<button class="cbi-button" style="padding:4px 12px;border-radius:6px;font-size:12px;background:rgba(245,54,92,.08);color:#f5365c;border:1px solid rgba(245,54,92,.2);cursor:pointer">删除</button>
					</td>
				</tr>
			</tbody>
		</table>

		<div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px">
			<button class="cbi-button cbi-button-add">+ 添加新规则</button>
		</div>

		<div class="cbi-page-actions">
			<button class="cbi-button cbi-button-reset">复位</button>
			<button class="cbi-button cbi-button-action">保存</button>
			<button class="cbi-button cbi-button-apply">保存并应用</button>
		</div>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-forwards.html").write_text(forwards_html, encoding="utf-8")
(cur_dir / "preview-forwards-dark.html").write_text(forwards_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 8. DHCP / DNS 预览 (网络 ➔ DHCP/DNS)
dhcp_html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>DHCP/DNS - UI 预览</title>
<style>
body {{ background:#f4f6fb; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; margin:0; padding:24px; }}
body[theme="dark"] {{ background:#181819; color:#d7dae0; }}
.cbi-map {{ max-width:1080px; margin:0 auto; }}
{dhcp_css}
</style></head>
<body>
<div id="cbi-dhcp" class="cbi-map">
	<div class="dhcp-head">
		<div class="dhcp-head-left">
			<h2>DHCP / DNS</h2>
		</div>
		<div class="dhcp-head-right">
			<div class="cbi-map-descr">管理局域网动态地址分配、静态 IP 绑定与 DNS 解析服务。</div>
		</div>
	</div>

	<ul class="cbi-tabmenu">
		<li class="cbi-tab"><a href="#">常规设置</a></li>
		<li><a href="#">静态地址分配</a></li>
		<li><a href="#">IP 集合</a></li>
		<li><a href="#">日志</a></li>
	</ul>

	<div class="cbi-section">
		<h4 style="margin:0 0 12px; font-size:15px; font-weight:600; color:var(--dhcp-text)">活跃 DHCP 租约</h4>
		<table id="lease_status_table">
			<thead>
				<tr>
					<th>主机名</th>
					<th>IPv4 地址</th>
					<th>MAC 地址</th>
					<th>租约剩余时间</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td><strong>MacBook-Pro.lan</strong></td>
					<td><code style="font-family:monospace; background:var(--dhcp-soft); padding:2px 6px; border-radius:4px">192.168.1.105</code></td>
					<td><code style="font-family:monospace; background:var(--dhcp-soft); padding:2px 6px; border-radius:4px">A4:83:E7:2B:91:02</code></td>
					<td><span style="color:var(--dhcp-ok); font-weight:600">11h 24m 10s</span></td>
				</tr>
				<tr>
					<td><strong>iPhone-15.lan</strong></td>
					<td><code style="font-family:monospace; background:var(--dhcp-soft); padding:2px 6px; border-radius:4px">192.168.1.118</code></td>
					<td><code style="font-family:monospace; background:var(--dhcp-soft); padding:2px 6px; border-radius:4px">3C:22:FB:4A:88:19</code></td>
					<td><span style="color:var(--dhcp-ok); font-weight:600">8h 05m 45s</span></td>
				</tr>
				<tr>
					<td><strong>TrueNAS-Core</strong></td>
					<td><code style="font-family:monospace; background:var(--dhcp-soft); padding:2px 6px; border-radius:4px">192.168.1.200</code></td>
					<td><code style="font-family:monospace; background:var(--dhcp-soft); padding:2px 6px; border-radius:4px">00:11:32:8A:2B:C4</code></td>
					<td><em>无限 (静态绑定)</em></td>
				</tr>
			</tbody>
		</table>

		<div class="cbi-page-actions">
			<button class="cbi-button cbi-button-reset">复位</button>
			<button class="cbi-button cbi-button-action">保存</button>
			<button class="cbi-button cbi-button-apply">保存并应用</button>
		</div>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-dhcp.html").write_text(dhcp_html, encoding="utf-8")
(cur_dir / "preview-dhcp-dark.html").write_text(dhcp_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 9. 生成 index.html 导航页
index_html = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LuCI 页面样式重构预览总览</title>
<style>
:root {
	--bg: #f4f6fb;
	--card: #fff;
	--border: #e9ecef;
	--text: #32325d;
	--muted: #8898aa;
	--primary: #5e72e4;
	--shadow: 0 4px 16px rgba(50,50,93,.08);
}
@media (prefers-color-scheme: dark) {
	:root {
		--bg: #181819;
		--card: #232324;
		--border: #3a3a3d;
		--text: #d7dae0;
		--muted: #9aa2ad;
		--shadow: 0 4px 16px rgba(0,0,0,.3);
	}
}
body {
	background: var(--bg);
	color: var(--text);
	font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
	margin: 0;
	padding: 40px 24px;
}
.container {
	max-width: 1040px;
	margin: 0 auto;
}
.header {
	margin-bottom: 32px;
}
h1 {
	font-size: 26px;
	margin: 0 0 8px;
	color: var(--text);
}
p.sub {
	color: var(--muted);
	font-size: 14px;
	margin: 0;
	line-height: 1.6;
}
.grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
	gap: 20px;
}
.card {
	background: var(--card);
	border: 1px solid var(--border);
	border-radius: 14px;
	padding: 22px;
	box-shadow: var(--shadow);
	display: flex;
	flex-direction: column;
	justify-content: space-between;
}
.card h2 {
	font-size: 18px;
	margin: 0 0 8px;
}
.card p {
	font-size: 13px;
	color: var(--muted);
	line-height: 1.6;
	margin: 0 0 16px;
	flex-grow: 1;
}
.links {
	display: flex;
	gap: 10px;
}
.btn {
	display: inline-block;
	flex: 1;
	text-align: center;
	padding: 8px 12px;
	border-radius: 8px;
	font-size: 13px;
	font-weight: 600;
	text-decoration: none;
	transition: all .15s ease;
}
.btn-light {
	background: var(--primary);
	color: #fff;
}
.btn-light:hover {
	filter: brightness(1.1);
}
.btn-dark {
	background: rgba(0,0,0,.08);
	color: var(--text);
	border: 1px solid var(--border);
}
@media (prefers-color-scheme: dark) {
	.btn-dark {
		background: rgba(255,255,255,.08);
	}
}
.btn-dark:hover {
	background: var(--border);
}
</style>
</head>
<body>
<div class="container">
	<div class="header">
		<h1>🎨 LuCI 页面样式重构预览总览</h1>
		<p class="sub">遵循 docs/UI-STYLE.md 规范打造的现代卡片化、无 Bootstrap、全深色自适应样式预览。</p>
	</div>
	<div class="grid">
		<div class="card">
			<div>
				<h2>易有云文件管理器</h2>
				<p>白卡头精简摘要、状态横向卡片（蓝主按钮+浅灰次按钮）、全局设置白卡化，并将保存操作底栏直接收纳进卡片右下方。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-linkease.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-linkease-dark.html">深色预览</a>
			</div>
		</div>
		<div class="card">
			<div>
				<h2>系统终端 (Web Terminal)</h2>
				<p>Web Terminal 仿窗口外壳、三色圆点装饰、新标签页全屏打开入口与自适应视口高度。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-ttyd.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-ttyd-dark.html">深色预览</a>
			</div>
		</div>
		<div class="card">
			<div>
				<h2>管理权 / 密码修改</h2>
				<p>卡片全宽铺满对齐，弱/中/强密码强度圆角胶囊徽章与右下方保存按钮。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-password.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-password-dark.html">深色预览</a>
			</div>
		</div>
		<div class="card">
			<div>
				<h2>系统进程 (Processes)</h2>
				<p>白卡容器与表头美化，支持输入命令名或 PID 即时搜索过滤，指标徽章与紧凑动作按钮组。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-processes.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-processes-dark.html">深色预览</a>
			</div>
		</div>
		<div class="card">
			<div>
				<h2>系统属性 (System Properties)</h2>
				<p>药丸标签栏 (Pill Tabs)、数字时钟小部件 (Live 呼吸绿点、浏览器同步与 NTP 同步操作组) 与表单卡片化。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-system.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-system-dark.html">深色预览</a>
			</div>
		</div>
		<div class="card">
			<div>
				<h2>SSH 密钥管理 (SSH-Keys)</h2>
				<p>虚线拖拽与粘贴密钥导入区、密钥凭据卡片化（算法胶囊、注释标题、等宽指纹与垃圾桶删除动作）。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-sshkeys.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-sshkeys-dark.html">深色预览</a>
			</div>
		</div>
		<div class="card">
			<div>
				<h2>防火墙 - 端口转发 (Port Forwards)</h2>
				<p>规则表格现代卡片化、区域流量流向胶囊 (WAN:port ➔ LAN:ip:port)、紧凑操作与添加按钮。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-forwards.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-forwards-dark.html">深色预览</a>
			</div>
		</div>
		<div class="card">
			<div>
				<h2>DHCP / DNS 与静态地址分配</h2>
				<p>活跃 DHCP 租约卡片表格、等宽 IP/MAC 标签、租约剩余时间胶囊与静态地址分配表格美化。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-dhcp.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-dhcp-dark.html">深色预览</a>
			</div>
		</div>
	</div>
</div>
</body>
</html>
"""
(cur_dir / "index.html").write_text(index_html, encoding="utf-8")

print("Generated all previews and index.html under docs/preview-ui/")
