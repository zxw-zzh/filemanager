# 基于Flask的文件管理系统

## 项目简介

本项目是一个基于 Flask 实现的现代化文件管理系统，支持 JWT 登录认证、文件/文件夹的浏览、上传、下载、删除、重命名、新建、搜索、分页、面包屑导航、目录树移动等功能。前端界面极简美观，交互友好，适合个人或团队在本地或服务器上部署使用。

**主要功能：**
- JWT 登录认证（用户名：admin，密码：admin@01）
- 目录分页浏览，支持自定义每页条数
- 递归查看文件夹内容，面包屑导航
- 文件/文件夹批量上传、文件夹整体上传、显示进度
- 文件/文件夹下载、删除、重命名、新建
- 文件/文件夹移动（支持目录树选择目标目录）
- 文件搜索
- 路径安全校验，防止目录遍历
- 现代化前端界面，极简美观，交互细腻
- 登录页全新美化，支持输入框图标、品牌色、响应式
- 全中文提示，用户体验友好
- 支持通过.env配置文件灵活管理端口、密钥、上传目录等

---

## 安装与部署

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/你的仓库名.git
cd filemanager
```

### 2. 安装依赖

建议使用 Python 3.7 及以上版本。

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python app.py
```

默认监听 `http://127.0.0.1:5000/`，可通过.env配置端口。

### 4. 访问系统

- 打开浏览器访问 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- 使用账号：admin，密码：admin@01 登录

---

## 目录结构说明

```
app.py                # Flask后端主程序
requirements.txt      # Python依赖
index.html            # 登录页面（极简美观）
home.html             # 文件管理主页面
config.js             # 前端API地址配置
favicon.ico           # 网站图标
/app/                 # 文件管理的根目录（所有操作都在此目录下进行）
```

---

## 常见问题

- **端口被占用**：修改 `.env` 或 `app.py` 中的端口号即可。
- **上传/下载失败**：请检查 `/app` 目录权限。
- **Token失效或接口401**：请重新登录获取新的Token。
- **批量/文件夹上传失败**：请使用现代浏览器（如Chrome/Edge）。
- **目录树移动失败**：请刷新页面或检查网络。

---

## 其他

如需二次开发或部署到服务器，建议使用 Nginx + Gunicorn 等方式进行生产部署。

---

如需更详细的说明或遇到问题，欢迎提Issue或联系作者！

---

## Docker一键部署

### 1. 构建镜像（推荐国内pip加速）

```bash
# 推荐先用清华源加速依赖安装
# Dockerfile中已内置：-i https://pypi.tuna.tsinghua.edu.cn/simple

docker build -t flask-filemanager .
```

### 2. 运行容器（推荐.env注入，安全灵活）

```bash
# 推荐用--env-file注入配置，镜像无需包含.env
# -p 5000:5000 映射端口
# --env-file .env 注入环境变量

docker run -d --name filemanager \
  --env-file .env \
  -p 5000:5000 \
  flask-filemanager
```

### 3. 数据持久化（可选，挂载本地目录）

```bash
# 挂载本地目录到容器内/app/app，实现文件持久化

docker run -d --name filemanager \
  --env-file .env \
  -p 5000:5000 \
  -v /your/local/dir:/app/app \
  flask-filemanager
```

### 4. 访问系统

浏览器访问：http://服务器IP:5000/
