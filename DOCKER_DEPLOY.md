# Docker 部署与直接部署区别说明

本项目支持两种部署方式：**Docker一键部署** 和 **传统直接部署**。两者在配置、启动、前端API地址适配等方面略有不同，现整理如下：

---

## 1. 目录结构与文件位置

- **Docker 部署**：所有代码、前端页面、配置文件（如config.js、index.html、app.py等）都被打包进镜像，运行时在容器内 `/app` 目录。
- **直接部署**：所有文件在本地物理机或服务器的项目目录下。

---

## 2. 配置文件管理

- **Docker 部署**：
  - 推荐用 `.env` 文件+`--env-file` 注入环境变量，镜像无需包含敏感配置。
  - 端口、上传目录、登录账号密码等均可在 `.env` 文件中灵活配置。
  - 运行命令示例：
    ```bash
    docker run -d --name filemanager \
      --env-file .env \
      -p 5000:5000 \
      flask-filemanager
    ```
- **直接部署**：
  - 直接在本地 `.env` 文件中配置，`python app.py` 启动即可。

---

## 3. 前端API地址适配

- **Docker 部署**：
  - `config.js` 已支持通过 `localStorage` 动态切换API地址。
  - 推荐在浏览器控制台执行：
    ```js
    localStorage.setItem('API_BASE_URL', 'http://服务器IP:5000')
    ```
    然后刷新页面。
  - 也可将 `config.js` 默认值改为自动适配当前域名：
    ```js
    window.API_BASE_URL = localStorage.getItem('API_BASE_URL') ||
      (window.location.protocol + '//' + window.location.hostname + ':5000');
    ```
- **直接部署**：
  - 若前后端同一台机器，默认 `127.0.0.1:5000` 即可。
  - 若分离部署，需手动修改 `config.js` 或用 `localStorage` 切换。

---

## 4. 数据持久化

- **Docker 部署**：
  - 推荐挂载本地目录到容器 `/app/app`，实现文件持久化：
    ```bash
    docker run -d --name filemanager \
      --env-file .env \
      -p 5000:5000 \
      -v /your/local/dir:/app/app \
      flask-filemanager
    ```
- **直接部署**：
  - 直接操作本地 `app` 目录即可。

---

## 5. 端口与防火墙

- **Docker 部署**：
  - 需确保宿主机5000端口对外开放。
- **直接部署**：
  - 本地开发可用127.0.0.1，生产环境需开放端口。

---

## 6. 启动/停止方式

- **Docker 部署**：
  - 启动：`docker run ...`
  - 停止：`docker stop filemanager && docker rm filemanager`
- **直接部署**：
  - 启动：`python app.py`
  - 停止：Ctrl+C 或 kill 进程

---

## 7. 日志与排错

- **Docker 部署**：
  - 查看日志：`docker logs filemanager`
  - 进入容器：`docker exec -it filemanager /bin/bash`
- **直接部署**：
  - 日志直接输出到终端。

---

## 8. 其它建议

- Docker 部署更适合云服务器、批量部署、环境隔离场景。
- 直接部署适合本地开发、调试。
- 如需多实例/负载均衡，推荐用 Docker Compose 或 K8s。

---

如有更多部署需求或遇到问题，欢迎随时咨询！ 