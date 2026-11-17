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

def extract_css(file_path):
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

ttyd_css = extract_css(".github/scripts/ttyd-ui/apply-ttyd.py")
pw_css = extract_css(".github/scripts/luci-mod-system-ui/apply-password.py")
proc_css = extract_css(".github/scripts/status-logs-ui/apply-processes.py")

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
			<h2>进程</h2>
			<div class="cbi-map-descr">查看当前系统运行的进程及其状态。</div>
		</div>
		<div class="proc-head-right">
			<span id="proc-count" class="proc-badge-count">3 进程</span>
			<input type="text" class="cbi-input-text proc-filter-input" placeholder="筛选...">
		</div>
	</div>
	<div class="proc-card">
		<table class="table">
			<tr class="tr table-titles">
				<th class="th">PID</th>
				<th class="th">所有者</th>
				<th class="th">命令</th>
				<th class="th">CPU 使用率 (%)</th>
				<th class="th">内存使用率 (%)</th>
				<th class="th right nowrap cbi-section-actions"></th>
			</tr>
			<tr class="tr">
				<td class="td"><span class="proc-badge-pid">1</span></td>
				<td class="td"><span class="proc-user">root</span></td>
				<td class="td"><span class="proc-cmd">/sbin/procd</span></td>
				<td class="td"><span class="proc-pct">0%</span></td>
				<td class="td"><span class="proc-pct">0.4%</span></td>
				<td class="td"><div class="proc-btn-group">
					<button class="btn cbi-button proc-btn proc-btn-hup">挂起</button>
					<button class="btn cbi-button proc-btn proc-btn-term">终止</button>
					<button class="btn cbi-button proc-btn proc-btn-kill">强杀</button>
				</div></td>
			</tr>
			<tr class="tr">
				<td class="td"><span class="proc-badge-pid">2841</span></td>
				<td class="td"><span class="proc-user">root</span></td>
				<td class="td"><span class="proc-cmd">/usr/sbin/tailscaled --state=/etc/tailscale/tailscaled.state</span></td>
				<td class="td"><span class="proc-pct proc-high">12.5%</span></td>
				<td class="td"><span class="proc-pct">2.1%</span></td>
				<td class="td"><div class="proc-btn-group">
					<button class="btn cbi-button proc-btn proc-btn-hup">挂起</button>
					<button class="btn cbi-button proc-btn proc-btn-term">终止</button>
					<button class="btn cbi-button proc-btn proc-btn-kill">强杀</button>
				</div></td>
			</tr>
			<tr class="tr">
				<td class="td"><span class="proc-badge-pid">3102</span></td>
				<td class="td"><span class="proc-user">root</span></td>
				<td class="td"><span class="proc-cmd">/usr/bin/ttyd -p 7681 login</span></td>
				<td class="td"><span class="proc-pct">0.1%</span></td>
				<td class="td"><span class="proc-pct">0.8%</span></td>
				<td class="td"><div class="proc-btn-group">
					<button class="btn cbi-button proc-btn proc-btn-hup">挂起</button>
					<button class="btn cbi-button proc-btn proc-btn-term">终止</button>
					<button class="btn cbi-button proc-btn proc-btn-kill">强杀</button>
				</div></td>
			</tr>
		</table>
	</div>
</div>
</body></html>"""
(cur_dir / "preview-processes.html").write_text(proc_html, encoding="utf-8")
(cur_dir / "preview-processes-dark.html").write_text(proc_html.replace('<body>', '<body theme="dark">'), encoding="utf-8")

# 4. 生成 index.html 导航页
index_html = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LuCI 样式重构预览总览</title>
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
	max-width: 900px;
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
	grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
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
		<h1>🎨 LuCI 页面样式重构预览</h1>
		<p class="sub">遵循 docs/UI-STYLE.md 规范打造的现代卡片化、无 Bootstrap、全深色自适应样式预览。</p>
	</div>
	<div class="grid">
		<div class="card">
			<div>
				<h2>系统终端</h2>
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
				<p>收敛至 680px 白卡容器，弱/中/强密码强度圆角胶囊徽章与对齐表单。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-password.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-password-dark.html">深色预览</a>
			</div>
		</div>
		<div class="card">
			<div>
				<h2>系统进程</h2>
				<p>白卡容器与表头美化，支持输入命令名或 PID 即时搜索过滤，指标徽章与紧凑动作按钮组。</p>
			</div>
			<div class="links">
				<a class="btn btn-light" href="preview-processes.html">浅色预览</a>
				<a class="btn btn-dark" href="preview-processes-dark.html">深色预览</a>
			</div>
		</div>
	</div>
</div>
</body>
</html>
"""
(cur_dir / "index.html").write_text(index_html, encoding="utf-8")

print("Generated all previews and index.html under docs/preview-ui/")
