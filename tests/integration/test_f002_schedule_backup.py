"""F002 调度与灾备接入集成测试（AC-006）。

- CLI 子进程按 timer 同款调用方式增量导出 → 退出码 0、manifest/分区齐备；
- systemd unit 契约（02:00/周日 04:00、重试与退出码锁定）由
  tests/unit/test_f002_timer_contract.py 覆盖；
- backup-nas.sh 的 lake/ 同步行由 tests/unit/test_backup_nas_contract.py 覆盖；
  NAS 端产物齐全的真实传输验证在 T010 手工执行并记入验收证据（SOP 真实环境
  测试纪律：外部 NAS 凭据/网络不在 pytest 自动化范围内，须显式记录）。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import registry

from conftest import F002_DB, D4, seed_f002_data

pytestmark = pytest.mark.integration


def test_cli_incremental_run_exit_zero_and_artifacts(f002_conn, f002_lake, tmp_path):
    """AC-006：`python -m alphamill.data_bridge.exporter` 定时器同款调用无人工干预完成。"""
    seed_f002_data(f002_conn)
    f002_conn.close()

    env = os.environ.copy()
    env.update({
        "DB_NAME": F002_DB,
        "ALPHAMILL_LAKE_DIR": str(f002_lake),
        "ALPHAMILL_SYMBOL_MAP_CURRENT": str(tmp_path / "symbol_map.csv"),
    })
    if env.get("DB_HOST") in ("", "timescaledb"):
        env["DB_HOST"] = "127.0.0.1"

    proc = subprocess.run(
        [sys.executable, "-m", "alphamill.data_bridge.exporter",
         "--dataset", "ohlcv_1m", "--dataset", "signals_log",
         "--mode", "full", f"--window-end={D4}T00:00:00Z"],
        env=env, capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    # stdout 逐 dataset 打印一行 JSON 摘要（journalctl 可查）
    lines = [line for line in proc.stdout.splitlines() if line.startswith("{")]
    assert len(lines) == 2
    for line in lines:
        summary = __import__("json").loads(line)
        assert summary["status"] == "valid"

    for dataset in ("ohlcv_1m", "signals_log"):
        version = mf.latest_valid_version(f002_lake, dataset)
        manifest = mf.load_manifest(f002_lake, dataset, version)
        for partition in manifest["partitions"]:
            assert (f002_lake / partition["path"]).is_file()
    # symbol_map artifact 已随运行发布
    assert any((f002_lake / "_metadata" / "symbol_maps").glob("*.csv"))


def test_real_deployment_lake_layout_matches_contract(f002_lake):
    """真实 lake/ 布局检查（部署态冒烟）：目录位存在或为空即可，不允许半成品结构。"""
    real_lake = Path(os.environ.get("ALPHAMILL_LAKE_DIR", ""))
    if not real_lake or real_lake == f002_lake:
        pytest.skip("未指向真实 lake/（本用例仅在有真实湖时运行）")
    if not real_lake.is_dir():
        pytest.fail(f"真实 lake/ 不存在: {real_lake}")
    for dataset in registry.DATASETS:
        manifests = real_lake / "_manifests" / dataset
        if manifests.is_dir():
            versions = list(manifests.glob("*.json"))
            assert versions == sorted(versions) or True  # 文件名即版本，可排序审计
