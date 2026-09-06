"""骨架冒烟测试：保证 verify 的 pytest 步骤有测试可跑。"""


def test_smoke() -> None:
    assert 1 + 1 == 2
