# 亚马逊SP API多店铺销售分析系统

## 📖 项目简介

这是一个**完整可部署**的亚马逊SP API多店铺销售分析系统，专为拥有100+店铺的卖家设计。

### ✨ 核心特性

- 🏪 **多店铺管理**: 支持100+店铺同时监控
- ⚡ **分钟级实时**: 每60秒更新一次数据
- 💾 **MySQL存储**: 按年月分表（如：orders_2024_01）
- 📊 **Web仪表板**: 实时数据可视化
- 🚀 **RESTful API**: 完整的API接口
- 📈 **数据分析**: 订单、销售、利润全面分析

## 🎯 功能模块

### 1. 数据库设计（按年月分表）

```
基础表：
- stores              # 店铺信息
- daily_summaries     # 每日汇总
- monitoring_snapshots # 监控快照
- alerts              # 告警记录

按月分表：
- orders_2024_01      # 2024年1月订单
- orders_2024_02      # 2024年2月订单
- sales_metrics_2024_01   # 2024年1月销售指标
- financial_events_2024_01 # 2024年1月财务事件
```

### 2. Web API接口

所有API接口前缀: `/api/v1`

**实时数据**
- `GET /realtime/overview` - 实时概览
- `GET /realtime/stores` - 所有店铺实时数据

**订单数据**
- `GET /orders/summary` - 订单汇总
- `GET /orders/trend` - 订单趋势

**销售数据**
- `GET /sales/summary` - 销售汇总
- `GET /sales/trend` - 销售趋势

**财务数据**
- `GET /finance/summary` - 财务汇总
- `GET /finance/profit-trend` - 利润趋势

**排名数据**
- `GET /rankings/stores` - 店铺排名

**告警数据**
- `GET /alerts` - 告警列表
- `PUT /alerts/{id}/acknowledge` - 确认告警

**仪表板**
- `GET /dashboard/overview` - 完整仪表板数据

### 3. Web界面

访问 `http://localhost:8000` 查看Web仪表板

- 实时概览卡片
- 24小时销售统计
- 订单/销售额趋势图
- 店铺排名TOP 10
- 最近告警列表

## 🚀 快速部署

### 方式一：一键部署（推荐）

```bash
# 1. 复制整个项目文件夹到您的服务器
scp -r amazon_sp_analytics user@your-server:/path/to/

# 2. 进入项目目录
cd amazon_sp_analytics

# 3. 运行部署脚本
chmod +x deploy.sh
./deploy.sh

# 4. 编辑配置文件
nano config.yaml  # 填入您的SP API凭证
nano .env         # 填入数据库配置

# 5. 启动服务
chmod +x start.sh
./start.sh
```

### 方式二：手动部署

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置文件
cp config.yaml.example config.yaml
cp .env.example .env
# 编辑配置文件

# 4. 初始化数据库
python3 scripts/init_database.py

# 5. 启动服务
python3 main.py
```

## ⚙️ 配置说明

### 1. 数据库配置 (.env)

```bash
# MySQL数据库连接
DATABASE_URL=mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4

# 示例
DATABASE_URL=mysql+pymysql://root:mypassword@localhost:3306/sp_analytics?charset=utf8mb4
```

### 2. 店铺配置 (config.yaml)

```yaml
stores:
  - store_id: store_001          # 唯一标识
    store_name: 美国主店铺        # 店铺名称
    client_id: amzn1.application-oa2-client.xxxxx
    client_secret: xxxxx
    refresh_token: Atzr|IwEBIxxxxx
    region: NA                    # NA=北美, EU=欧洲, FE=远东
    marketplace_ids:
      - ATVPDKIKX0DER             # 美国市场
    enabled: true                 # 是否启用
```

### 3. 获取SP API凭证

1. 登录 [Amazon Seller Central](https://sellercentral.amazon.com/)
2. 进入"开发者中心" > "添加新应用"
3. 填写应用信息获取 `Client ID` 和 `Client Secret`
4. 授权应用获取 `Refresh Token`

详细步骤: https://developer-docs.amazon.com/sp-api/docs/registering-your-application

## 📊 数据库表结构

### 按月分表命名规则

- **订单表**: `orders_YYYY_MM` (例: orders_2024_01)
- **销售指标表**: `sales_metrics_YYYY_MM`
- **财务事件表**: `financial_events_YYYY_MM`

### 优势

1. **性能优化**: 查询只扫描相关月份的表
2. **数据归档**: 方便按月归档历史数据
3. **维护便捷**: 单表数据量可控
4. **扩展性好**: 自动创建未来月份的表

## 🌐 Web界面使用

### 实时监控

系统每60秒自动更新数据，包括：
- 最近1小时订单统计
- 订单速率（单/小时）
- 收入速率（$/小时）
- 平均订单价值

### 趋势分析

- 30天订单趋势图
- 30天销售额趋势图
- 支持缩放和交互

### 店铺排名

- 按销售额排名
- 按订单量排名
- 显示占比和进度条

## 📡 API调用示例

### 获取实时数据

```javascript
// 获取最近60分钟的实时概览
fetch('/api/v1/realtime/overview?minutes=60')
  .then(res => res.json())
  .then(data => {
    console.log('总店铺数:', data.total_stores);
    console.log('1小时订单:', data.total_orders_1h);
    console.log('订单速率:', data.orders_per_hour);
  });
```

### 获取订单趋势

```javascript
// 获取最近30天订单趋势
const endDate = new Date().toISOString();
const startDate = new Date(Date.now() - 30*24*60*60*1000).toISOString();

fetch(`/api/v1/orders/trend?start_date=${startDate}&end_date=${endDate}&granularity=day`)
  .then(res => res.json())
  .then(data => {
    console.log('趋势数据:', data);
  });
```

### 获取店铺排名

```javascript
// 获取销售额TOP 10店铺
fetch('/api/v1/rankings/stores?metric=revenue&top_n=10')
  .then(res => res.json())
  .then(data => {
    data.forEach(store => {
      console.log(`${store.rank}. ${store.store_name}: $${store.value}`);
    });
  });
```

## 🔧 系统要求

### 硬件要求

- **CPU**: 2核心以上
- **内存**: 4GB以上（100店铺建议8GB）
- **磁盘**: 50GB以上（取决于数据保留周期）

### 软件要求

- **操作系统**: Linux / macOS / Windows
- **Python**: 3.8+
- **MySQL**: 5.7+ 或 8.0+
- **Redis**: 6.0+ (可选)

## 📂 项目结构

```
amazon_sp_analytics/
├── app/
│   ├── api/              # FastAPI路由和schemas
│   ├── analytics/        # SP API分析模块
│   ├── cache/            # Redis缓存
│   ├── config/           # 配置管理
│   ├── core/             # SP API客户端
│   ├── models/           # 数据库模型
│   ├── services/         # 业务服务
│   └── utils/            # 工具模块
├── static/               # 静态文件
│   ├── css/             # 样式表
│   └── js/              # JavaScript
├── templates/            # HTML模板
├── logs/                 # 日志文件
├── scripts/              # 脚本工具
├── main.py              # 主程序入口
├── config.yaml          # 店铺配置
├── .env                 # 环境变量
├── requirements.txt     # Python依赖
├── deploy.sh            # 部署脚本
├── start.sh             # 启动脚本
└── README.md            # 本文档
```

## 🐛 故障排除

### 问题1: 数据库连接失败

```bash
# 检查MySQL服务
sudo systemctl status mysql

# 测试连接
mysql -u root -p -h localhost
```

### 问题2: SP API认证失败

- 检查 `client_id` 和 `client_secret` 是否正确
- 确认 `refresh_token` 未过期
- 验证 `region` 设置正确

### 问题3: 端口占用

```bash
# 修改 .env 中的 PORT
PORT=8080

# 或查找并关闭占用8000端口的进程
lsof -i :8000
kill -9 <PID>
```

## 📈 性能优化

### 针对100+店铺

1. **启用Redis缓存** - 减少数据库查询
2. **定时任务** - 设置合理的数据采集间隔（建议60秒）
3. **数据归档** - 定期归档1年前的历史数据
4. **索引优化** - 确保常用查询字段有索引

### 数据库优化

```sql
-- 查看表大小
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)"
FROM information_schema.TABLES
WHERE table_schema = 'sp_analytics'
ORDER BY (data_length + index_length) DESC;

-- 优化表
OPTIMIZE TABLE orders_2024_01;
```

## 📝 更新日志

### v1.0.0 (2024-10-07)

- ✅ 初始版本发布
- ✅ 按年月分表设计
- ✅ Web仪表板
- ✅ RESTful API
- ✅ 实时监控
- ✅ 100+店铺支持

## 📄 许可证

本项目基于 Apache License 2.0 许可证开源。

## 🤝 支持

如有问题，请提交Issue或联系技术支持。

---

**注意**: 
1. 请妥善保管 `config.yaml` 和 `.env` 文件，不要提交到版本控制系统
2. 首次部署建议使用沙箱环境测试
3. 定期备份数据库