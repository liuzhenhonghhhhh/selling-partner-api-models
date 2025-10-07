# 功能特性详细说明

## 🎯 核心功能列表

### 1️⃣ 订单分析功能

#### 1.1 实时订单监控
- **功能描述**: 以分钟为单位监控订单变化
- **适用场景**: 高频店铺、促销活动期间
- **主要指标**:
  - 订单数量
  - 订单金额
  - 订单速率（单/小时）
  - 收入速率（$/小时）
  - 平均订单价值（AOV）

```python
# 获取最近60分钟的订单指标
metrics = orders_analytics.get_order_metrics_realtime(
    marketplace_ids=marketplace_ids,
    time_window_minutes=60
)
```

#### 1.2 订单状态分析
- **订单状态追踪**:
  - PendingAvailability (预订待发货)
  - Pending (待付款)
  - Unshipped (未发货)
  - PartiallyShipped (部分发货)
  - Shipped (已发货)
  - InvoiceUnconfirmed (发票未确认)
  - Canceled (已取消)
  - Unfulfillable (无法履行)

- **按状态统计**:
  - 各状态订单数量
  - 各状态订单金额
  - 状态转换趋势

#### 1.3 订单渠道分析
- **FBA vs FBM**:
  - Amazon配送订单 (AFN)
  - 卖家配送订单 (MFN)
  - 渠道占比分析
  - 渠道绩效对比

#### 1.4 订单时间分析
- **时间维度**:
  - 按小时统计
  - 按天统计
  - 按周统计
  - 按月统计

- **应用场景**:
  - 识别高峰时段
  - 优化库存管理
  - 调整促销策略

#### 1.5 订单详情获取
- **订单信息**:
  - 订单ID
  - 购买日期
  - 订单状态
  - 收货地址
  - 买家信息
  - 支付方式
  - 配送方式

- **订单商品**:
  - ASIN
  - SKU
  - 数量
  - 单价
  - 折扣
  - 税费

---

### 2️⃣ 销售数据分析

#### 2.1 销售指标统计
- **核心指标**:
  - 订单数 (Order Count)
  - 销售件数 (Unit Count)
  - 销售额 (Total Sales)
  - 平均订单价值 (AOV)
  - 平均件/单 (UPO)

#### 2.2 时间粒度分析
- **支持的粒度**:
  - 小时 (Hour) - 适用于实时监控
  - 天 (Day) - 适用于日常分析
  - 周 (Week) - 适用于周报
  - 月 (Month) - 适用于月报
  - 年 (Year) - 适用于年度报告
  - 总计 (Total) - 适用于汇总统计

```python
# 按小时获取销售数据
hourly_sales = sales_analytics.get_sales_by_hour(
    marketplace_ids=marketplace_ids,
    start_time=start_time,
    end_time=end_time
)
```

#### 2.3 买家类型分析
- **B2B vs B2C**:
  - B2B订单统计
  - B2C订单统计
  - All（全部）

#### 2.4 增长率计算
- **对比分析**:
  - 订单增长率
  - 销售额增长率
  - 件数增长率
  - AOV增长率

```python
# 对比本周与上周
growth = sales_analytics.calculate_growth_rate(
    marketplace_ids=marketplace_ids,
    current_days=7,
    comparison_days=7
)
```

#### 2.5 时间序列数据
- **趋势分析**:
  - 销售趋势图数据
  - 移动平均
  - 季节性分析
  - 异常检测

---

### 3️⃣ 财务与利润分析

#### 3.1 收入分析
- **收入构成**:
  - 商品售价 (Principal)
  - 运费收入 (Shipping)
  - 礼品包装费 (GiftWrap)
  - 促销返还 (Promotion)
  - 税费 (Tax)

```python
profit = finance_analytics.get_profit_analysis(days=7)
print(profit['revenue_breakdown'])
# {'Principal': 50000, 'Shipping': 5000, ...}
```

#### 3.2 费用分析
- **费用类型**:
  - FBA配送费 (FBAPerUnitFulfillmentFee)
  - 佣金 (Commission)
  - 退款管理费 (RefundCommission)
  - 仓储费 (Storage)
  - 长期仓储费 (LongTermStorage)
  - 移除费 (Removal)
  - 处置费 (Disposal)

#### 3.3 利润计算
- **计算公式**:
  ```
  毛利润 = 总收入 - 总费用
  净利润 = 毛利润 - 退款
  利润率 = (净利润 / 总收入) × 100%
  ```

#### 3.4 退款分析
- **退款统计**:
  - 退款笔数
  - 退款金额
  - 退款率
  - 退款原因分析

#### 3.5 财务事件
- **事件类型**:
  - 发货事件 (Shipment)
  - 退款事件 (Refund)
  - 调整事件 (Adjustment)
  - 服务费事件 (ServiceFee)
  - 追溯收费 (Retrocharge)
  - 租赁交易 (RentalTransaction)

---

### 4️⃣ 多店铺聚合功能

#### 4.1 数据汇总
- **支持汇总的指标**:
  - 总店铺数
  - 总订单数
  - 总销售额
  - 总利润
  - 平均AOV
  - 平均利润率

```python
# 获取所有店铺的销售数据
all_sales = sales_analytics.get_all_stores_sales_dashboard(hours=24)
print(f"总店铺: {all_sales['total_stores']}")
print(f"总销售额: ${all_sales['total_sales']:,.2f}")
```

#### 4.2 店铺排名
- **排名维度**:
  - 按订单量排名
  - 按销售额排名
  - 按利润排名
  - 按利润率排名
  - 按增长率排名

```python
# 获取销售额前10的店铺
top_stores = sales_analytics.get_top_performing_stores(
    hours=24,
    metric='total_sales',
    top_n=10
)
```

#### 4.3 区域分析
- **按区域聚合**:
  - 北美区 (NA)
  - 欧洲区 (EU)
  - 远东区 (FE)

#### 4.4 店铺对比
- **横向对比**:
  - 同时段各店铺表现
  - 店铺绩效差异
  - 最佳实践识别

#### 4.5 异常检测
- **检测维度**:
  - 订单量异常下降
  - 利润率异常偏低
  - 退款率异常偏高
  - 库存异常

---

### 5️⃣ 实时监控功能

#### 5.1 后台监控
- **监控机制**:
  - 独立线程运行
  - 可配置更新间隔
  - 自动数据采集
  - 历史数据保存

```python
monitor = RealtimeMonitor(
    multi_store_client=multi_store_client,
    update_interval=60  # 每60秒更新一次
)
monitor.start()
```

#### 5.2 告警系统
- **告警触发条件**:
  - 订单量低于阈值
  - 利润率低于阈值
  - 订单金额异常
  - API调用失败

```python
# 设置告警阈值
monitor.set_alert_threshold("min_orders_per_hour", 10)
monitor.set_alert_threshold("min_profit_margin", 5)

# 添加告警回调
def alert_handler(alerts):
    for alert in alerts:
        send_email(alert['message'])
        send_sms(alert['message'])

monitor.add_alert_callback(alert_handler)
```

#### 5.3 指标历史
- **历史数据**:
  - 保存最近1000个数据点
  - 支持时间范围查询
  - 趋势分析
  - 数据导出

#### 5.4 实时仪表板
- **仪表板数据**:
  - 概览指标
  - 店铺排名
  - 时间序列图
  - 告警列表

```python
dashboard = DashboardData(monitor)
overview = dashboard.get_overview_dashboard()
rankings = dashboard.get_store_rankings()
```

---

### 6️⃣ 缓存机制

#### 6.1 Redis缓存
- **缓存策略**:
  - 自动缓存API响应
  - 可配置TTL
  - 命名空间隔离
  - 批量操作

```python
from cache import init_cache

cache = init_cache(host='localhost', port=6379)
cache.set('namespace', 'key', data, ttl=300)
data = cache.get('namespace', 'key')
```

#### 6.2 内存缓存备选
- **特性**:
  - 无需Redis依赖
  - 自动降级
  - 适用于小规模部署

#### 6.3 缓存装饰器
```python
from cache import cached

@cached(namespace="orders", ttl=60)
def get_orders(store_id, marketplace_id):
    # 自动缓存返回结果
    return fetch_orders_from_api()
```

#### 6.4 缓存管理
- **管理功能**:
  - 清空命名空间
  - 检查缓存存在
  - 获取TTL
  - 批量删除

---

### 7️⃣ 性能优化

#### 7.1 限流管理
- **API限流**:
  - 自动遵守SP API速率限制
  - 令牌桶算法
  - 突发流量支持
  - 自动重试

#### 7.2 并发处理
- **优化建议**:
  - 使用异步IO (aiohttp)
  - 多线程并发
  - 批量处理店铺
  - 连接池管理

#### 7.3 数据压缩
- **减少数据量**:
  - 只获取必要字段
  - 使用分页
  - 增量更新
  - 数据归档

---

## 📊 使用场景

### 场景1: 大促实时监控
```python
# 双11、黑五等大促期间
monitor = RealtimeMonitor(
    multi_store_client=multi_store_client,
    update_interval=60  # 每分钟更新
)

# 设置低订单量告警
monitor.set_alert_threshold("min_orders_per_hour", 1000)

# 启动监控
monitor.start()
```

### 场景2: 每日运营报告
```python
# 生成昨日运营报告
yesterday = datetime.now() - timedelta(days=1)
start = yesterday.replace(hour=0, minute=0, second=0)
end = yesterday.replace(hour=23, minute=59, second=59)

# 订单数据
orders = orders_analytics.get_orders(
    marketplace_ids=marketplace_ids,
    created_after=start.isoformat(),
    created_before=end.isoformat()
)

# 销售数据
sales = sales_analytics.get_sales_by_day(
    marketplace_ids=marketplace_ids,
    start_date=start,
    end_date=end
)

# 生成报告
generate_daily_report(orders, sales)
```

### 场景3: 利润优化分析
```python
# 分析最近30天的利润构成
profit = finance_analytics.get_profit_analysis(days=30)

# 识别高费用商品
high_fee_items = identify_high_fee_items(profit['fee_breakdown'])

# 优化建议
recommendations = generate_optimization_recommendations(high_fee_items)
```

### 场景4: 多店铺绩效对比
```python
# 对比所有店铺表现
all_stores = sales_analytics.get_all_stores_sales_dashboard(hours=24)

# 找出表现最好和最差的店铺
best_store = max(all_stores['store_dashboards'], key=lambda x: x['total_sales'])
worst_store = min(all_stores['store_dashboards'], key=lambda x: x['total_sales'])

# 分析差异原因
analyze_performance_gap(best_store, worst_store)
```

---

## 🔮 未来功能规划

### 即将推出
- [ ] 库存预警功能
- [ ] 价格竞争分析
- [ ] 客户评价分析
- [ ] 广告投放ROI分析
- [ ] 自动化报告邮件
- [ ] Web仪表板界面
- [ ] 移动端App

### 长期规划
- [ ] AI智能预测
- [ ] 自动补货建议
- [ ] 动态定价优化
- [ ] 多渠道数据整合
- [ ] 区块链数据验证

---

## 💡 最佳实践

### 1. 针对100+店铺的优化
```python
# 分批处理，避免超时
batch_size = 20
for i in range(0, len(stores), batch_size):
    batch = stores[i:i+batch_size]
    process_batch(batch)
    time.sleep(1)  # 避免过快
```

### 2. 缓存策略
```python
# 根据数据更新频率设置TTL
config.cache_ttl = {
    'orders': 60,        # 订单1分钟
    'sales_metrics': 300, # 销售5分钟
    'finances': 1800,     # 财务30分钟
}
```

### 3. 错误处理
```python
try:
    orders = orders_analytics.get_orders(...)
except Exception as e:
    logger.error(f"获取订单失败: {e}")
    # 使用缓存数据
    orders = cache.get('orders', cache_key)
```

### 4. 日志管理
```python
# 配置日志
logger.add(
    "logs/sp_api_{time}.log",
    rotation="1 day",      # 每天轮换
    retention="30 days",   # 保留30天
    level="INFO"
)
```

---

## 📈 性能指标

| 指标 | 目标值 | 说明 |
|-----|-------|------|
| API响应时间 | < 2s | 单次API调用 |
| 数据更新延迟 | < 60s | 实时监控延迟 |
| 缓存命中率 | > 80% | 减少API调用 |
| 并发店铺数 | 100+ | 同时支持店铺数 |
| 系统可用性 | 99.9% | 年度可用性 |

---

本文档持续更新中...