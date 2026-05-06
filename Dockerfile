# PT-Accelerator Dockerfile
# 多架构构建：amd64 + arm64

FROM node:24-slim AS frontend-builder

WORKDIR /frontend

# 安装前端依赖并构建
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

ENV APP_PORT=23333 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 复制前端构建产物
COPY --from=frontend-builder /frontend/dist ./dist

# 创建运行目录
RUN mkdir -p logs cache CFST

EXPOSE $APP_PORT

# 修正：直接运行 main.py（已在 WORKDIR /app）
CMD ["python", "main.py"]
