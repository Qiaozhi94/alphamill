"""F009 客户端交付边的**服务端侧契约**（unit，CI 常绿）。

对应 spec FR-009 / AC-010、architecture §7.1「客户端分动作超时」：

服务端拥有三个动作 deadline 的缺省值，并规定**客户端 deadline 必须严格大于同一动作的
服务端 deadline**（缺省 +5s 余量）。两端同值时客户端先抛 `OSError`，服务端规范的
`E_TIMEOUT` 信封根本收不到——那条信封是"动作仍在进行"的唯一告知渠道，收不到就等于
客户端把"仍在进行"误判成"连接坏了"（检视 R4-002）。

**边界**：本文件只断言服务端这一侧——缺省值、余量规则、与配置载荷的一致性。客户端
实现的五项（分动作超时、预算与 `vram_readable` 分账、余量、`restore_required` 触发、
`transitional` fail-closed）由 F003 分支的 `test_f003_gpu_slot.py` /
`test_f003_cli_contract.py` 承载并在那里做变异判红——那些文件依赖 F003 的客户端代码，
本分支不存在，交付边记录见 F009 tasks T014/T021（代码检视 R1-006 的裁决）。
"""

from __future__ import annotations

import pytest

from alphamill.kronos_service import lifecycle_config

EXPECTED_SERVER_DEADLINES = {"status": 5.0, "stop": 60.0, "restore": 120.0}


def test_server_deadline_defaults_match_contract_table() -> None:
    assert lifecycle_config.SERVER_DEADLINES == EXPECTED_SERVER_DEADLINES


def test_defaults_are_consistent_with_loaded_config() -> None:
    """契约表与实际配置载荷不得各说一套。"""
    cfg = lifecycle_config.load_config({})

    assert cfg.status_timeout_s == lifecycle_config.SERVER_DEADLINES["status"]
    assert cfg.stop_timeout_s == lifecycle_config.SERVER_DEADLINES["stop"]
    assert cfg.restore_timeout_s == lifecycle_config.SERVER_DEADLINES["restore"]


@pytest.mark.parametrize("action", ["status", "stop", "restore"])
def test_client_deadline_floor_is_strictly_greater(action: str) -> None:
    """客户端 deadline 下限必须**严格大于**服务端同动作 deadline。"""
    server = lifecycle_config.SERVER_DEADLINES[action]
    floor = lifecycle_config.client_deadline_floor(action)

    assert floor > server, f"{action}: 客户端下限 {floor} 未严格大于服务端 {server}"
    assert floor == server + lifecycle_config.CLIENT_DEADLINE_MARGIN_S


def test_client_deadline_floors_are_pairwise_distinct() -> None:
    """三个动作的值互不相同：共用单一超时会用 status 的量级去卡 stop（FR-009）。"""
    floors = [lifecycle_config.client_deadline_floor(a) for a in EXPECTED_SERVER_DEADLINES]

    assert len(set(floors)) == len(floors), floors


def test_zero_margin_is_rejected() -> None:
    """余量为 0 即两端同值：客户端先超时，收不到 E_TIMEOUT 信封。"""
    with pytest.raises(lifecycle_config.ConfigError):
        lifecycle_config.client_deadline_floor("stop", margin_s=0.0)

    with pytest.raises(lifecycle_config.ConfigError):
        lifecycle_config.client_deadline_floor("stop", margin_s=-1.0)


def test_unknown_action_is_rejected() -> None:
    with pytest.raises(lifecycle_config.ConfigError):
        lifecycle_config.client_deadline_floor("reboot")


def test_configured_server_deadline_shifts_the_floor() -> None:
    """服务端改配置后，客户端下限随之上移——否则迁移执行机时余量会被吃掉。"""
    cfg = lifecycle_config.load_config({"KRONOS_LIFECYCLE_STOP_TIMEOUT_S": "300"})

    floor = lifecycle_config.client_deadline_floor("stop", server_deadline_s=cfg.stop_timeout_s)

    assert floor == 305.0
