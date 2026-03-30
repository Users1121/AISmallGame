# 多智能体联合项目游戏 - 项目结构说明

## 项目概述
这是一个末日生存题材的多智能体策略游戏，三个AI领导人（DeepSeek、阿里云百炼、MiniMax）分别以不同的治理理念领导幸存者，通过博弈决定人类文明的未来。

## 目录结构

```
leadergame/
├── backend/                    # 后端服务
│   ├── ai_agents/             # AI智能体模块
│   │   ├── deepseek/         # DeepSeek AI实现
│   │   ├── aliyun/           # 阿里云百炼AI实现
│   │   └── minimax/          # MiniMax AI实现
│   ├── game_engine/          # 游戏核心引擎
│   │   ├── war/              # 战争系统
│   │   ├── events/           # 随机事件系统
│   │   ├── resources/        # 资源管理系统
│   │   └── diplomacy/        # 外交系统
│   ├── api/                  # API接口层
│   │   ├── routes/           # 路由定义
│   │   └── middleware/       # 中间件
│   ├── models/               # 数据模型
│   │   ├── entities/         # 实体定义
│   │   └── schemas/          # 数据模式
│   └── utils/                # 工具函数
│       ├── logger/           # 日志工具
│       └── config/           # 配置工具
│
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/       # 组件库
│   │   │   ├── game/        # 游戏相关组件
│   │   │   ├── ui/          # UI基础组件
│   │   │   └── chat/        # 聊天组件
│   │   ├── pages/           # 页面组件
│   │   │   ├── home/        # 首页
│   │   │   ├── game/        # 游戏主界面
│   │   │   └── settings/    # 设置页面
│   │   ├── services/        # 服务层
│   │   │   ├── api/         # API调用
│   │   │   └── websocket/   # WebSocket连接
│   │   ├── stores/          # 状态管理
│   │   │   ├── game/        # 游戏状态
│   │   │   └── chat/        # 聊天状态
│   │   └── styles/          # 样式文件
│   │       └── themes/      # 主题配置
│   └── public/              # 静态资源
│       ├── assets/          # 资源文件
│       └── icons/           # 图标文件
│
├── config/                   # 配置文件
│   ├── ai/                  # AI配置
│   ├── game/                # 游戏配置
│   └── server/              # 服务器配置
│
├── docs/                     # 文档
│   ├── api/                 # API文档
│   ├── design/              # 设计文档
│   └── user/                # 用户文档
│
├── data/                     # 数据文件
├── logs/                     # 日志文件
└── prepare (2).txt          # 项目需求文档

## 核心模块说明

### AI智能体模块 (backend/ai_agents/)
- **deepseek/**: 仁心AI，以德治国，注重人民幸福
- **aliyun/**: 铁腕AI，严刑峻法，崇尚武力扩张
- **minimax/**: 神谕AI，宗教治国，精神控制

### 游戏引擎模块 (backend/game_engine/)
- **war/**: 战争机制，包括宣战、战斗、第三方干预
- **events/**: 随机事件池，自然灾害、社会事件、外交事件
- **resources/**: 资源管理，食物、能源、零件的生产与消耗
- **diplomacy/**: 外交系统，关系等级、外交行动、助战机制

### 前端组件 (frontend/src/components/)
- **game/**: 地图、雷达图、时间轴等游戏核心组件
- **ui/**: 按钮、面板、弹窗等基础UI组件
- **chat/**: 与AI领导人聊天的聊天框组件

### 状态管理 (frontend/src/stores/)
- **game/**: 游戏状态，包括三国属性、资源、时间等
- **chat/**: 聊天状态，包括消息记录、当前对话对象等

## 技术栈建议

### 后端
- Python + FastAPI (API框架)
- WebSocket (实时通信)
- asyncio (异步处理)

### 前端
- React + TypeScript
- Zustand 或 Redux (状态管理)
- WebSocket (实时通信)
- Canvas 或 SVG (地图渲染)

## 数据流

1. AI决策 → 游戏引擎计算 → 更新游戏状态
2. 游戏状态变化 → WebSocket推送 → 前端更新UI
3. 玩家操作 → API请求 → 后端处理 → 返回结果
4. 聊天消息 → AI处理 → 返回回复 → 前端显示

## 开发建议

1. 先实现核心游戏引擎（资源、属性、事件）
2. 再实现三个AI的基本决策逻辑
3. 最后完善前端UI和交互
4. 注意API密钥的安全存储（使用环境变量）
