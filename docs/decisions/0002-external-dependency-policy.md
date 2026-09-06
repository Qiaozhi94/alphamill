# ADR-0002：外部依赖管理策略 —— vendor / fork / 原样依赖三分法

- 日期：2026-09-06
- 状态：Accepted
- 决策人：Georg
- 操作细节：[`docs/alphamill-integration.md`](../alphamill-integration.md) §五

## 背景

AlphaMill 引入四个开源项目：AlphaGen（挖掘引擎）、Freqtrade（执行）、Vibe-Trading（研究上层）、
Kronos（时序基础模型）。需要统一"改谁、不改谁、怎么跟上游"的规则。

判断原则：**改动深度决定集成距离**。fork 仅适用于"要上游全部功能 + 必须改核心 + 上游不收 PR"
的窄缝——四个引入项没有一个落在缝里。

## 决策

| 引入项 | 方式 | 要点 |
|---|---|---|
| AlphaGen | **vendor** 进主仓 | 动大手术（换数据层/现代化）+ 上游冻结 + 只用子集 |
| Freqtrade | 原样依赖（官方 docker 镜像 + `user_data/` 插件层） | 零源码改动；pin 镜像 tag；上游 bug 走 issue + monkey-patch 过渡 |
| Vibe-Trading | 原样依赖（pip pin + 本机 CLI/服务） | 只碰 4 个配置层接入面；pin 小版本，里程碑边界才升级 |
| Kronos 模型代码 | 原样依赖（上游 fresh clone + pin commit） | 零改动；权重走 HuggingFace；服务薄壳为本仓 `kronos_service/` |

**永不 fork。**

vendor 卫生规则（AlphaGen 专用）：

1. vendor 目录内最小 diff，贴近上游原貌，每处修改标注 `# [alphamill] <原因>`；
2. 胶水代码（feather→tensor 适配器、FactorDef 包装）放 vendor 外，保持可整体替换；
3. `alphagen_vendor/VENDORED.md` 记录上游 repo + commit hash、vendor 日期、修改清单、许可说明；
4. 上游若复活且需新特性，按修改清单手工重移植。

升级纪律：依赖版本 pin；只在里程碑边界升级；升级后先跑冒烟再继续实验（保证实验结果可比）。

## 后果

- 正面：主仓自包含（不依赖旧仓/上游存活）；维护面最小化；实验可复现性强。
- 负面：AlphaGen 放弃上游更新（冻结代码 vendor 后由本项目全权维护）；Freqtrade/Vibe-Trading
  行为受上游发布节奏约束。
