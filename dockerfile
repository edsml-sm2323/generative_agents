# 使用 Python 作为基础镜像
FROM python:3.9.12-slim

# 设置工作目录
WORKDIR /generative_agents

# 复制项目文件到容器内
COPY . /generative_agents

# 安装依赖：首先安装后端依赖
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# # 安装 Node.js 和前端依赖
# RUN apt-get update && apt-get install -y curl
# RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && apt-get install -y nodejs
# WORKDIR /generative_agents/environment/frontend_ui
# RUN npm install

# 返回到项目根目录，暴露后端和前端端口
WORKDIR /generative_agents
EXPOSE 8000 8080

# 启动后端和前端
# CMD ["sh", "-c", "python3 manage.py runserver 0.0.0.0:8000 & npm run serve --prefix environment/frontend_ui"]
CMD ["sh", "-c", "python3 ./environment/frontend_server/manage.py runserver 0.0.0.0:8000"]

