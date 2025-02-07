FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建static目录
RUN mkdir -p static

# 先复制static目录
COPY static/ static/
# 再复制其他文件
COPY app.py .

EXPOSE 5000

# 修改启动命令，增加workers和超时设置
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
