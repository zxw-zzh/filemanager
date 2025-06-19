# 基于官方Python镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖和代码
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .

# 自动创建上传目录（可通过环境变量覆盖）
RUN mkdir -p /app/app

# 复制.env（如有）
#COPY .env .

# 设置环境变量（可被docker run -e覆盖）
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "app.py"] 