# Shared Web Cache Simulator


这是一个基于请求轨迹（trace-driven）的共享 Web 缓存模拟器，**不是真实的 HTTP 代理**，不需要发送网络请求。

本仓库仅提供文件骨架，缓存逻辑、替换策略、模拟流程、指标计算和测试自行实现。

## 文件结构

```text
shared-web-cache-simulator/
├── README.md
├── requirements.txt
├── data/
│   └── sample_requests.csv
├── src/
│   ├── main.py
│   ├── cache.py
│   ├── simulator.py
│   ├── metrics.py
│   └── policies/
│       ├── fifo.py
│       ├── lru.py
│       ├── lfu.py
│       └── custom.py
└── tests/
    └── test_cache.py
```

## 文件用途

- `src/main.py`：程序入口。
- `src/cache.py`：共享缓存的数据结构与基本操作。
- `src/simulator.py`：读取请求轨迹，按顺序驱动模拟。
- `src/metrics.py`：统计缓存命中、未命中等指标。
- `src/policies/fifo.py`：先进先出替换策略。
- `src/policies/lru.py`：最近最少使用替换策略。
- `src/policies/lfu.py`：最不经常使用替换策略。
- `src/policies/custom.py`：小组自行设计的替换策略。
- `tests/test_cache.py`：缓存相关测试。

## 示例数据

`data/sample_requests.csv` 每行表示一次请求，按文件中的顺序处理：

- `timestamp`：模拟时间（秒）。
- `client_id`：发出请求的客户端编号；多个客户端共享同一个缓存。
- `url`：资源标识，仅用于模拟，无需访问。
- `size_bytes`：资源大小（字节）。

示例包含不同客户端对相同资源的重复请求，方便以后检查共享缓存行为。

## 开始开发

1. 安装 Python 3。
2. 在项目目录中打开终端。
3. 按需填写各个 Python 文件；目前它们只有说明和 TODO，没有可运行的模拟逻辑。
4. 如果以后使用第三方库，在 `requirements.txt` 中记录依赖。

当前没有第三方依赖，也没有实现任何测试。
