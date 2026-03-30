# 快速启动指南

## 方式一：使用启动脚本（推荐）

双击运行 `start.bat` 文件，脚本会自动启动后端和前端服务。

## 方式二：手动启动

### 1. 启动后端服务

打开第一个终端窗口，执行：

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 启动

### 2. 启动前端服务

打开第二个终端窗口，执行：

```bash
cd frontend
npm run dev
```

前端将在 http://localhost:3000 启动

## 访问应用

- 前端应用：http://localhost:3000
- 后端API文档：http://localhost:8000/docs

## 停止服务

在对应的终端窗口按 `Ctrl + C` 停止服务

## 注意事项

1. 确保已安装 Python 3.8+ 和 Node.js 16+
2. 确保已安装后端和前端依赖
3. 确保8000和3000端口未被占用
4. 如果遇到问题，请查看 README.md 中的故障排除部分
