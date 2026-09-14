FROM python:3.11-slim AS mock

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

EXPOSE 8001
CMD ["uvicorn", "alphamill.kronos_service.server:app", "--host", "0.0.0.0", "--port", "8001"]

# real 目标：在 mock 之上叠加 Kronos 推理依赖（design §2 锁定的宿主 AC-006 实测集）。
FROM mock AS real
# torch 走 CPU wheel index；其余从 PyPI 安装上游直接 import 的最小集
# （model/kronos.py → torch/huggingface_hub/tqdm，model/module.py → einops）。

RUN pip install --no-cache-dir torch==2.14.0 \
    --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir \
    einops==0.8.2 \
    safetensors==0.8.0 \
    huggingface_hub==1.31.0 \
    tqdm==4.70.0
