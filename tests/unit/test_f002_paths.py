"""F002 湖路径边界测试。"""

import pytest

from alphamill.data_bridge import paths
from alphamill.data_bridge.errors import DataBridgeError


@pytest.mark.parametrize("value", ["../escape", "nested/value", r"nested\\value", ""])
def test_partition_dimension_cannot_escape_lake(tmp_path, value):
    with pytest.raises(DataBridgeError, match="非法分区路径组件"):
        paths.partition_dir(tmp_path, "ohlcv_1m", {"exchange": value})
