"""T017/T018：systemd timer 单元契约（调度时刻、重试与退出码锁定指令）。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "deployment"

UNITS = {
    "export": {"mode": "incremental", "calendar": "*-*-* 02:00:00"},
    "fullexport": {"mode": "full", "calendar": "Sun *-*-* 04:00:00"},
}


def _read(name: str) -> str:
    return (DEPLOYMENT / name).read_text(encoding="utf-8")


def test_service_units_exist_with_full_retry_contract():
    for name, spec in UNITS.items():
        service = _read(f"alphamill-{name}.service")
        assert "Type=oneshot" in service, name
        assert "Restart=on-failure" in service, name
        assert "RestartSec=15min" in service, name
        # StartLimit 必须显式声明（backup.service 疏漏教训，design §5）
        assert "StartLimitIntervalSec=" in service, name
        assert "StartLimitBurst=3" in service, name
        # 对账失败（退出码 2）锁定不重试
        assert "RestartPreventExitStatus=2" in service, name
        assert "-m alphamill.data_bridge.exporter" in service, name
        assert f"--mode {spec['mode']}" in service, name


def test_timer_units_schedule_and_persistence():
    export_timer = _read("alphamill-export.timer")
    assert "OnCalendar=*-*-* 02:00:00" in export_timer
    assert "Persistent=true" in export_timer
    assert "WantedBy=timers.target" in export_timer
    assert "02:00" in export_timer  # 排序约束注释自证

    full_timer = _read("alphamill-fullexport.timer")
    assert "OnCalendar=Sun *-*-* 04:00:00" in full_timer
    assert "Persistent=true" in full_timer


def test_export_services_use_venv_python():
    for name in UNITS:
        service = _read(f"alphamill-{name}.service")
        assert "ExecStart=%h/projects/alphamill/.venv/bin/python" in service, name
        assert "WorkingDirectory=%h/projects/alphamill" in service, name
        # 调度进程不继承用户 shell 环境，库凭据必须经 EnvironmentFile 注入
        assert "EnvironmentFile=%h/projects/alphamill/deployment/.env" in service, name
