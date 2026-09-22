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
# torch 的版本与 wheel 索引由构建参数驱动（F010 FR-001）：缺省 = CPU wheel；GPU 构建由
# deployment/docker-compose.gpu.yml 只覆盖索引为 cu130（CPU/GPU 同版本）。ARG 须声明在
# 本 stage 内（stage 作用域）。其余从 PyPI 安装上游直接 import 的最小集
# （model/kronos.py → torch/huggingface_hub/tqdm，model/module.py → einops）。
ARG TORCH_VERSION=2.14.0
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir torch==${TORCH_VERSION} \
    --index-url ${TORCH_INDEX_URL} \
 && pip install --no-cache-dir \
    einops==0.8.2 \
    safetensors==0.8.0 \
    huggingface_hub==1.31.0 \
    tqdm==4.70.0
