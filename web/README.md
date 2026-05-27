# WorldQuant Brain Web

基于 `wqb` 库的 WorldQuant Brain 平台 Web 可视化界面。

## 快速开始

### 前置条件

- Python 3.13+
- Node.js 20+

### 安装

```bash
# 后端
cd web/backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 运行

```bash
cd web
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

打开 `http://localhost:8000`，输入 WorldQuant Brain 账号密码登录。

### 开发模式

前端热更新：

```bash
cd web/frontend
npm run dev
```

后端热更新：

```bash
cd web
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 功能

- 认证管理（登录/登出/状态）
- 数据集搜索与详情查看
- 数据字段浏览
- 算子浏览器
- Alpha 管理（列表筛选、详情、属性编辑）
- Alpha 模拟（单次/批量）
- Alpha 检查与提交

## 技术栈

- 后端：FastAPI + WQBSession
- 前端：Vue 3 + Vite + Naive UI
- 通信：REST API + WebSocket
