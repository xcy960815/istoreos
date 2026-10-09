# 家庭服务器改造总背景（2026-10 启动）

> **面向后续 AI 助手**：本文档记录用户整个家庭基础设施改造的完整背景。
> 处理本仓库任何事务（裁剪配置、构建固件、调整路由器服务）之前，先读这一篇，
> 再读 [`CUSTOM-TRIMMING.md`](CUSTOM-TRIMMING.md)（裁剪决策）和根目录 [`BUILD-CUSTOM.md`](../BUILD-CUSTOM.md)（构建流程）。

## 一、为什么改造

用户家里的网络核心是一台 **J4125 软路由（iStoreOS）**，它原本身兼数职：既是主路由，又用 Docker 跑着一套「数据中台」（Oracle、SQL Server、MySQL×2、ClickHouse、Postgres、Qdrant 向量库、embedding 服务、Prometheus 监控等约 25 个容器）。后果：

- 8G 内存被吃掉 4.4G，**Oracle 反复被 OOM 杀死**
- 数据库与路由争抢资源，路由稳定性受威胁
- 该机器是家里最弱的 CPU，跑这类服务先天不足

因此决定：**把全部 Docker 服务迁到性能更强的 9400F，路由器回归纯路由**，并顺手规划全家设备梯队。

## 二、全家设备清单与最终定位

| 设备 | 配置 | 定位 | 状态（2026-10-05） |
|---|---|---|---|
| **J4125 软路由**（本固件目标机，4×2.5G i226-V） | 8G 内存 / 128G 盘 | 纯网关 + Tailscale 入口 + 公网 DDNS-Go + VLAN 分段 | 服务迁出后刷裁剪版固件（即本仓库产物） |
| **9400F 主机** | 16G DDR4-2666 / 512G SSD / 450W / GTX 1060 6G | **家庭主服务器**：接盘全部 Docker 服务 | 计划装 Ubuntu Server 24.04.5，执行迁移 |
| **零刻 N100 小主机** | N100 / 单槽 DDR5 / 暂无内存硬盘 | 哨兵节点：异地备份 + 独立监控 + 备用 Tailscale 入口 + k3s 练手 | 等内存好价上岗（8G DDR5-4800 即可） |
| **12600KF 新机** | 6P+4E / B660M DDR4 + 新 DDR4-3200 16G | 用户新主力机 | 先用 1060 过渡点亮 |
| **MacBook Pro 16** | M1 Max / 32G | 用户日常开发机 | 不当服务器（ARM 跑不了 x86 容器） |

## 三、网络架构

- 家庭网段 `192.168.100.0/24`，网关 = J4125（192.168.100.1）
- **远程两条路并行**：① 家人设备走 **Tailscale**（路由器 `100.116.149.47`，已开 exit node；网内有 iPhone、两台 MacBook）；② **公网域名走 DDNS-Go**（宽带有公网 IP + 免费域名，网关必须开箱带 DDNS-Go）。不要写成「只用 Tailscale、不用 DDNS」。公网入口用防火墙手动端口转发，不上 UPnP、不用 OpenWrt 自带 `luci-app-ddns`、不用 ddnsto
- 9400F 装好后将 DHCP 静态绑定 **192.168.100.10**，有线接路由器 LAN 口
- **四口规划**：口1 WAN｜口2 LAN 主交换机｜口3 服务器 2.5G 专线（9400F 加二手 2.5G 网卡）｜口4 备胎（N100/12600KF）
- 计划做 VLAN 分段：IoT/访客与主网隔离（家里有对外服务，安全加固）
- 宽带 ≤ 千兆，J4125 纯路由绰绰有余（需开 flow offload）

## 四、Docker 服务迁移（iStoreOS → 9400F）

迁移的容器（原在路由器上，由 DPanel 管理，7 个 compose 项目）：

- **数据中台（dms）**：应用本体 + Prometheus + SQL Server 2022 + Oracle 23ai + MySQL×2 + Redis×2 + ClickHouse + Postgres + Qdrant + infinity embedding + cadvisor + node-exporter
- 其他：atvloadly（需 avahi）、cliproxyapi、study-java 全家桶、new-api、iptv-checker、watchtower

要点：

- 数据全部是 **bind mount**（无 named volume）：`/mnt/sata1-4/AppData`（11.4G）、`/mnt/sata1-4/Configs/DPanel/compose`、`/opt/data-middle-station`（186M）
- 新机把数据盘挂到**相同路径 `/mnt/sata1-4`**，compose 零修改
- 停容器后 rsync（数据库目录必须停机拷贝）
- qdrant(6333)/embedding(7997) 原绑定路由器 IP，迁移后改绑新 IP

## 五、AI / 影音升级计划

- embedding 现状：J4125 CPU 跑 `bge-small-zh-v1.5`（2400 万参数）
- 迁移后：**bge-m3**（5.7 亿）+ ONNX int8 引擎（infinity `--engine optimum`）；1060 回到 9400F 后可上 GPU，灌库快 10–50 倍
- ⚠️ 换模型 = 向量维度变化（512→1024），**Qdrant 需全量重灌**——趁迁移一步到位
- 影音：Jellyfin 先 CPU 软转；1060 回服务器后 NVENC 硬转；远期 N100 Quick Sync

## 六、相关机器的后续计划

- **9400F**：Ubuntu Server 24.04.5（ISO 已下载校验）→ Docker 迁移 → bge-m3 → Tailscale 入网
- **12600KF**：B660M DDR4 + 新 DDR4-3200 16G（⚠️ 9400F 的 DDR4 一根不能拔，DDR4 已暴涨）；显卡先用 1060 过渡 → 闲鱼收二手 RTX 3060 12G → 1060 回服务器
- **N100**：哨兵岗位四件套（restic/borg 异地备份、Uptime-Kuma+Grafana 独立监控、Tailscale 第二入口、双节点 k3s 练手）；8G DDR5-4800 + 512G NVMe 即可上岗；远期可刷 iStoreOS 接班软路由

## 七、功耗账（用户关注点）

- 9400F 服务器 7×24：待机 30–40W，月电费 14–20 元
- N100 替代回本期 8–10 年（内存 1500 元 vs 每月省 10–15 元）→ 等内存好价，不硬换
- 省电三板斧：无卡启动拔亮机卡 / C-State + powertop / 非日常数据库定时启停

## 八、行动清单（截至 2026-10-05）

- [ ] 9400F 装 Ubuntu Server（U 盘 Ventoy + ISO 已备好）
- [ ] DHCP 绑定 192.168.100.10；测试无卡启动
- [ ] 停容器 → rsync 三目录 → compose 起服务 → 验证
- [ ] embedding 换 bge-m3 → Qdrant 重灌
- [ ] 9400F 装 Tailscale 入网
- [ ] 12600KF 组装（B660M DDR4 + 1060 过渡）
- [ ] 闲鱼收 3060 12G → 1060 回服务器
- [ ] 数据库备份体系（先本地，N100 到位后异地）
- [ ] **iStoreOS 裁剪版构建 + 刷入（本仓库，最后做）**
- [ ] N100 蹲内存好价上岗

## 九、相关资料索引

| 资料 | 位置 |
|---|---|
| 裁剪决策记录 | 本仓库 `docs/CUSTOM-TRIMMING.md` |
| 构建与刷机流程 | 本仓库 `BUILD-CUSTOM.md` |
| 云端构建 | GitHub Actions（手动触发，见 `.github/workflows/`） |
| compose 文件合集 | `github.com/xcy960815/istoreos-compose`（本地 `~/Documents/my-repositories/istoreos-compose`） |
| 用户个人完整笔记 | 坚果云 `note/家庭服务器改造方案_2026-10-05.md` |
