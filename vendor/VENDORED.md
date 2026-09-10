# VENDORED 第三方上游资产

> 待遇与 Freqtrade 相同（migration-plan §三）：各自上游仓，零改动，我们不维护 fork。

| 资产 | 上游 | pin commit | 落盘位置 | 引入日期 |
|---|---|---|---|---|
| Kronos 模型代码 | https://github.com/shiyu-coder/Kronos | `67b630e67f6a18c9e9be918d9b4337c960db1e9a` | `vendor/Kronos/`（git 本地-only，见 .gitignore） | 2026-09-10 |
| Kronos-Tokenizer-base 权重 | https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base | snapshot（safetensors + config） | `models/Kronos-Tokenizer-base/`（git 本地-only） | 2026-09-10 |
| Kronos-base 权重 | https://huggingface.co/NeoQuasar/Kronos-base | snapshot（safetensors + config） | `models/Kronos-base/`（git 本地-only） | 2026-09-10 |

## 更新流程

1. `git -C vendor/Kronos fetch --tags && git -C vendor/Kronos checkout <新 commit>`
2. 更新本表 pin commit 与日期，提交本文件。
3. 权重更新走 `huggingface_hub.snapshot_download`，人工核对文件清单后同样只更新本表。

> 服务薄壳（`src/alphamill/kronos_service/`）通过 `KRONOS_*` 环境变量指向 `models/` 路径；
> GPU 未就绪时 `KRONOS_DEVICE=cpu`（spec FR-003 / T003 决策）。
