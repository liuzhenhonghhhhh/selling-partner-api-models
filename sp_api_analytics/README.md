# 亚马逊SP API多店铺销售分析系统

## 📖 简介

这是一个专为拥有多个亚马逊店铺的卖家设计的**实时销售数据分析系统**，支持：

✨ **核心特性**
- 🏪 **多店铺管理**: 支持100+店铺同时监控
- ⚡ **分钟级实时**: 销量数据以分钟为单位更新
- 📊 **全面分析**: 订单、销售、利润、库存全方位分析
- 🔄 **自动刷新**: LWA令牌自动管理，无需手动维护
- 🚀 **高性能**: 内置限流器和缓存机制
- 📈 **实时监控**: 后台持续监控，支持自定义告警

## 🎯 功能模块

### 1. 订单分析 (Orders API)
- ✅ 实时订单监控（分钟级）
- ✅ 订单状态追踪
- ✅ 每日/每小时订单量统计
- ✅ 订单地域分布分析
- ✅ 订单详情和商品信息获取
- ✅ 周期对比分析

### 2. 销售数据分析 (Sales API)
- ✅ 按小时/天/周/月聚合销售数据
- ✅ 销售额趋势分析
- ✅ 平均订单价值(AOV)计算
- ✅ 单位数量和总销售额统计
- ✅ 增长率计算
- ✅ 店铺排名分析

### 3. 财务与利润分析 (Finances API)
- ✅ 收入与费用明细
- ✅ 利润计算（收入-费用-退款）
- ✅ 利润率分析
- ✅ FBA费用细分
- ✅ 退款和退货统计
- ✅ 周期利润对比

### 4. 多店铺聚合
- ✅ 所有店铺数据汇总
- ✅ 店铺表现排名
- ✅ 跨店铺对比分析
- ✅ 区域市场分析

### 5. 实时监控
- ✅ 后台持续数据采集
- ✅ 自定义告警阈值
- ✅ 指标历史记录
- ✅ 实时仪表板

### 6. 数据缓存
- ✅ Redis缓存支持
- ✅ 内存缓存备选
- ✅ 灵活的TTL配置
- ✅ 命名空间管理

## 🚀 快速开始

### 1. 安装依赖

```bash
cd sp_api_analytics
pip install -r requirements.txt
```

### 2. 配置店铺信息

首次运行会自动生成配置模板 `stores_config.yaml`：

```yaml
global:
  redis_host: localhost
  redis_port: 6379
  database_url: sqlite:///sp_api_analytics.db
  log_level: INFO

stores:
  - store_id: store_001
    store_name: 美国主店铺
    client_id: your_client_id_here
    client_secret: your_client_secret_here
    refresh_token: your_refresh_token_here
    region: NA
    marketplace_ids:
      - ATVPDKIKX0DER  # 美国市场
    enabled: true
    
  - store_id: store_002
    store_name: 欧洲店铺
    client_id: your_client_id_here
    client_secret: your_client_secret_here
    refresh_token: your_refresh_token_here
    region: EU
    marketplace_ids:
      - A1F83G8C2ARO7P  # 英国
      - A1PA6795UKMFR9  # 德国
    enabled: true
```

### 3. 获取SP API凭证

参考[官方文档](https://developer-docs.amazon.com/sp-api/docs/registering-your-application)注册应用并获取：
- `client_id`: LWA Client ID
- `client_secret`: LWA Client Secret  
- `refresh_token`: 刷新令牌

### 4. 运行主程序

```bash
python main.py
```

## 💡 使用示例

### 示例1: 单店铺订单分析

```python
from config import StoreCredentials, SPAPIConfig, Region, MARKETPLACES
from core import SPAPIClient
from analytics import OrdersAnalytics

# 创建店铺凭证
credentials = StoreCredentials(
    store_id="my_store_001",
    store_name="我的美国店铺",
    client_id="your_client_id",
    client_secret="your_client_secret",
    refresh_token="your_refresh_token",
    region=Region.NA,
    marketplace_ids=[MARKETPLACES["US"].marketplace_id]
)

# 创建客户端
config = SPAPIConfig()
client = SPAPIClient(credentials, config)

# 创建订单分析器
orders_analytics = OrdersAnalytics(client)

# 获取最近24小时的订单
recent_orders = orders_analytics.get_recent_orders(
    marketplace_ids=credentials.marketplace_ids,
    hours=24
)

# 分析订单
analysis = orders_analytics.analyze_orders(recent_orders)
print(f"总订单数: {analysis['total_orders']}")
print(f"总金额: ${analysis['total_amount']:,.2f}")
```

### 示例2: 实时订单监控（分钟级）

```python
# 获取最近60分钟的实时指标
realtime_metrics = orders_analytics.get_order_metrics_realtime(
    marketplace_ids=credentials.marketplace_ids,
    time_window_minutes=60
)

print(f"订单速率: {realtime_metrics['orders_per_hour']:.2f} 单/小时")
print(f"收入速率: ${realtime_metrics['revenue_per_hour']:,.2f}/小时")
```

### 示例3: 多店铺销售分析

```python
from core import MultiStoreClient
from analytics import MultiStoreSalesAnalytics

# 创建多店铺客户端
multi_store_client = MultiStoreClient(config)
multi_store_client.add_store(credentials1)
multi_store_client.add_store(credentials2)
# ... 添加更多店铺

# 创建多店铺销售分析器
clients = multi_store_client.get_all_clients()
sales_analytics = MultiStoreSalesAnalytics(clients)

# 获取所有店铺的销售仪表板
dashboard = sales_analytics.get_all_stores_sales_dashboard(hours=24)

print(f"总店铺数: {dashboard['total_stores']}")
print(f"总销售额: ${dashboard['total_sales']:,.2f}")
```

### 示例4: 利润分析

```python
from analytics import FinanceAnalytics

finance_analytics = FinanceAnalytics(client)

# 获取最近7天的利润分析
profit = finance_analytics.get_profit_analysis(days=7)

print(f"收入: ${profit['revenue']:,.2f}")
print(f"费用: ${profit['fees']:,.2f}")
print(f"净利润: ${profit['net_profit']:,.2f}")
print(f"利润率: {profit['profit_margin']:.2f}%")
```

### 示例5: 启动实时监控

```python
from utils import RealtimeMonitor

# 创建监控器
monitor = RealtimeMonitor(
    multi_store_client=multi_store_client,
    update_interval=60  # 每分钟更新
)

# 设置告警阈值
monitor.set_alert_threshold("min_orders_per_hour", 10)
monitor.set_alert_threshold("min_profit_margin", 5)

# 添加告警回调
def alert_handler(alerts):
    for alert in alerts:
        print(f"[{alert['severity']}] {alert['message']}")

monitor.add_alert_callback(alert_handler)

# 启动监控
monitor.start()

# ... 监控在后台运行 ...

# 获取最新指标
latest = monitor.get_latest_metrics()
print(latest.metrics)
```

## 📊 支持的市场

| 区域 | 国家 | Marketplace ID | 代码 |
|------|------|----------------|------|
| 北美 | 美国 | ATVPDKIKX0DER | US |
| 北美 | 加拿大 | A2EUQ1WTGCTBG2 | CA |
| 北美 | 墨西哥 | A1AM78C64UM0Y8 | MX |
| 欧洲 | 英国 | A1F83G8C2ARO7P | UK |
| 欧洲 | 德国 | A1PA6795UKMFR9 | DE |
| 欧洲 | 法国 | A13V1IB3VIYZZH | FR |
| 欧洲 | 意大利 | APJ6JRA9NG5V4 | IT |
| 欧洲 | 西班牙 | A1RKKUPIHCS9HS | ES |
| 远东 | 日本 | A1VC38T7YXB528 | JP |
| 远东 | 澳大利亚 | A39IBJ37TRP1C6 | AU |
| 远东 | 新加坡 | A19VAU5U5O7RUS | SG |

## ⚙️ 配置说明

### 限流配置

系统内置SP API限流器，确保不超过API速率限制：

| API | 速率 (请求/秒) | 突发 |
|-----|---------------|------|
| Orders API | 0.0167 | 20 |
| Sales API | 0.5 | 15 |
| Finances API | 0.5 | 30 |
| Reports API | 0.0222 | 10 |
| Products API | 2 | 10 |
| Inventory API | 2 | 10 |

### 缓存配置

默认缓存TTL设置：

| 数据类型 | TTL (秒) | 说明 |
|---------|---------|------|
| 订单 | 60 | 1分钟 |
| 销售指标 | 300 | 5分钟 |
| 财务数据 | 1800 | 30分钟 |
| 库存 | 600 | 10分钟 |
| 价格 | 300 | 5分钟 |

## 🏗️ 系统架构

```
sp_api_analytics/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── sp_api_config.py   # 配置管理
├── core/                   # 核心模块
│   ├── __init__.py
│   └── sp_client.py       # SP API客户端
├── analytics/              # 分析模块
│   ├── __init__.py
│   ├── orders_analytics.py    # 订单分析
│   ├── sales_analytics.py     # 销售分析
│   └── finance_analytics.py   # 财务分析
├── cache/                  # 缓存模块
│   ├── __init__.py
│   └── redis_cache.py     # Redis缓存
├── utils/                  # 工具模块
│   ├── __init__.py
│   └── monitor.py         # 实时监控
├── examples/               # 示例代码
│   └── basic_usage.py
├── main.py                # 主程序
├── requirements.txt       # 依赖
└── README.md             # 文档
```

## 🔧 高级用法

### 自定义缓存

```python
from cache import init_cache

# 初始化Redis缓存
cache = init_cache(
    host='localhost',
    port=6379,
    db=0,
    password=None
)

# 使用缓存
cache.set('namespace', 'key', {'data': 'value'}, ttl=300)
data = cache.get('namespace', 'key')
```

### 周期对比分析

```python
# 订单对比
comparison = orders_analytics.compare_with_previous_period(
    marketplace_ids=marketplace_ids,
    current_hours=24
)

print(f"订单变化: {comparison['changes']['orders_change_percent']:+.2f}%")
print(f"收入变化: {comparison['changes']['revenue_change_percent']:+.2f}%")
```

### 店铺排名

```python
# 获取表现最好的店铺
top_stores = sales_analytics.get_top_performing_stores(
    hours=24,
    metric='total_sales',
    top_n=10
)

for i, store in enumerate(top_stores, 1):
    print(f"{i}. {store['store_name']}: ${store['total_sales']:,.2f}")
```

## 📈 性能优化建议

### 针对100+店铺的优化

1. **并发采集**: 使用异步IO或多线程同时采集多个店铺数据
2. **缓存策略**: 合理设置缓存TTL，减少API调用
3. **批量处理**: 尽可能批量处理店铺数据
4. **限流管理**: 遵守API限流，避免被限速
5. **增量更新**: 只获取变化的数据，不重复获取

### 分钟级监控建议

```python
# 针对分钟级监控，建议：
# 1. 使用较短的时间窗口（如最近60分钟）
# 2. 设置合理的更新间隔（如60秒）
# 3. 启用Redis缓存减少API调用

monitor = RealtimeMonitor(
    multi_store_client=multi_store_client,
    update_interval=60  # 每分钟更新一次
)
```

## 🛡️ 安全建议

1. **凭证管理**: 
   - ❌ 不要将凭证硬编码到代码中
   - ✅ 使用配置文件或环境变量
   - ✅ 不要提交 `stores_config.yaml` 到版本控制

2. **访问控制**:
   - 限制配置文件权限
   - 使用最小权限原则

3. **日志安全**:
   - 不要在日志中输出敏感信息
   - 定期清理历史日志

## ❓ 常见问题

### Q1: 如何处理API限流？
A: 系统内置了限流器，会自动遵守SP API的速率限制。如果遇到429错误，系统会自动重试。

### Q2: 支持多少个店铺？
A: 理论上支持无限个店铺，但建议根据实际API限流情况控制在100-200个店铺。

### Q3: 数据更新频率是多少？
A: 订单数据可以实现分钟级更新，销售和财务数据建议5-30分钟更新一次。

### Q4: 是否支持沙箱环境？
A: 支持，在配置中设置 `region: SANDBOX` 即可。

### Q5: 如何获取历史数据？
A: Orders API支持最近2年数据（部分市场仅支持2016年后数据）。

## 📝 更新日志

### v1.0.0 (2024-10-07)
- ✨ 初始版本发布
- ✅ 支持订单、销售、财务分析
- ✅ 支持多店铺聚合
- ✅ 支持实时监控
- ✅ 支持Redis缓存

## 📄 许可证

本项目基于 Apache License 2.0 许可证开源。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues
- Email: your-email@example.com

---

**注意**: 使用本系统需要有效的亚马逊SP API凭证。请确保遵守亚马逊的服务条款和API使用政策。