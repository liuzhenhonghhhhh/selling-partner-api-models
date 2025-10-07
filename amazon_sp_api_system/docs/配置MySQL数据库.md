# 📊 MySQL数据库配置指南

## 🎯 概述

本系统使用**MySQL数据库**存储亚马逊SP API的销售和库存数据，并通过**Reports API批量获取数据**，比单独调用API效率高得多。

## 📋 前置要求

### 1. 安装MySQL数据库

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

**Mac**:
```bash
brew install mysql
brew services start mysql
```

**Windows**:
下载并安装 [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)

### 2. 创建数据库和用户

登录MySQL:
```bash
mysql -u root -p
```

执行以下SQL命令:
```sql
-- 创建数据库
CREATE DATABASE amazon_sp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'amazon_user'@'localhost' IDENTIFIED BY '你的密码';

-- 授权
GRANT ALL PRIVILEGES ON amazon_sp.* TO 'amazon_user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

## ⚙️ 配置系统

### 1. 修改配置文件

创建或编辑 `amazon_sp_analytics/config.yaml`:

```yaml
# MySQL数据库配置
database:
  type: mysql  # 使用MySQL
  host: localhost
  port: 3306
  user: amazon_user
  password: 你的密码
  database: amazon_sp
  charset: utf8mb4
  echo: false  # 是否打印SQL语句
  auto_create_tables: true  # 自动创建数据表

# 报告调度配置
scheduler:
  enabled: true  # 是否启用定时任务
  
  # 销售报告
  sales_report:
    enabled: true
    schedule_time: "02:00"  # 每天凌晨2点执行
    days_ago: 1  # 获取最近1天的数据
  
  # 库存报告
  inventory_report:
    enabled: true
    schedule_time: "03:00"  # 每天凌晨3点执行
    days_ago: 1

# 店铺配置（从配置管理界面添加）
stores: []
```

### 2. 安装Python依赖

```bash
cd amazon_sp_analytics
pip install -r requirements.txt
```

依赖包括:
- `pymysql` - MySQL驱动
- `sqlalchemy` - ORM框架
- `schedule` - 定时任务
- `fastapi`, `uvicorn` - Web框架
- 其他...

## 🗂️ 数据库表结构

系统会自动创建以下数据表:

### 1. stores - 店铺表
存储店铺基本信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| store_id | VARCHAR(100) | 店铺唯一标识 |
| store_name | VARCHAR(200) | 店铺名称 |
| region | VARCHAR(20) | 区域(NA/EU/FE) |
| marketplace_ids | JSON | Marketplace ID列表 |
| enabled | BOOLEAN | 是否启用 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 2. sales_reports - 销售报告(按日期)
存储每日销售和流量数据

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键ID |
| store_id | VARCHAR(100) | 店铺ID |
| report_date | DATETIME | 报告日期 |
| marketplace_id | VARCHAR(50) | 市场ID |
| ordered_product_sales | FLOAT | 订购产品销售额 |
| units_ordered | INT | 订购数量 |
| total_order_items | INT | 订单项总数 |
| page_views | INT | 页面浏览量 |
| sessions | INT | 会话数 |
| buy_box_percentage | FLOAT | Buy Box获取率 |
| ... | ... | 更多字段 |

### 3. sales_reports_by_asin - 销售报告(按ASIN)
存储每个产品(ASIN)的销售数据

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键ID |
| store_id | VARCHAR(100) | 店铺ID |
| parent_asin | VARCHAR(20) | 父ASIN |
| child_asin | VARCHAR(20) | 子ASIN |
| sku | VARCHAR(100) | SKU |
| units_ordered | INT | 订购数量 |
| ordered_product_sales | FLOAT | 销售额 |
| sessions | INT | 会话数 |
| ... | ... | 更多字段 |

### 4. inventory_reports - 库存报告(汇总)
存储库存汇总数据

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键ID |
| store_id | VARCHAR(100) | 店铺ID |
| report_start_date | DATETIME | 报告开始日期 |
| report_end_date | DATETIME | 报告结束日期 |
| sellable_on_hand_inventory_units | INT | 可售库存数量 |
| unsellable_on_hand_inventory_units | INT | 不可售库存数量 |
| sell_through_rate | FLOAT | 销售通过率 |
| ... | ... | 更多字段 |

### 5. inventory_reports_by_asin - 库存报告(按ASIN)
存储每个产品的库存数据

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键ID |
| store_id | VARCHAR(100) | 店铺ID |
| asin | VARCHAR(20) | ASIN |
| sellable_on_hand_inventory_units | INT | 可售库存数量 |
| ... | ... | 更多字段 |

### 6. report_requests - 报告请求记录
存储报告请求的状态和历史

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键ID |
| store_id | VARCHAR(100) | 店铺ID |
| report_type | VARCHAR(100) | 报告类型 |
| report_id | VARCHAR(100) | 亚马逊报告ID |
| status | VARCHAR(50) | 状态 |
| requested_at | DATETIME | 请求时间 |
| downloaded_at | DATETIME | 下载时间 |
| ... | ... | 更多字段 |

## 🚀 启动系统

### 方式1: 使用主程序

创建 `amazon_sp_analytics/run_with_scheduler.py`:

```python
import logging
from app.config.sp_api_config import MultiStoreConfig
from app.models.mysql_manager import create_mysql_manager_from_config
from app.services.report_scheduler import ReportScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# MySQL配置
mysql_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'amazon_user',
    'password': '你的密码',
    'database': 'amazon_sp',
    'charset': 'utf8mb4',
    'auto_create_tables': True
}

# 初始化
config_manager = MultiStoreConfig()
db_manager = create_mysql_manager_from_config(mysql_config)
scheduler = ReportScheduler(config_manager, db_manager)

# 设置定时任务
scheduler.schedule_sales_reports(time_str="02:00", days_ago=1)
scheduler.schedule_inventory_reports(time_str="03:00", days_ago=1)

# 启动调度器
scheduler.start()

print("✅ 报告调度器已启动")
print("📊 每天 02:00 自动获取销售报告")
print("📦 每天 03:00 自动获取库存报告")

# 保持运行
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("\n停止调度器...")
    scheduler.stop()
```

运行:
```bash
python run_with_scheduler.py
```

### 方式2: 手动执行报告任务

创建 `amazon_sp_analytics/manual_report.py`:

```python
from app.config.sp_api_config import MultiStoreConfig
from app.models.mysql_manager import create_mysql_manager_from_config
from app.services.report_service import ReportProcessingService

# MySQL配置
mysql_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'amazon_user',
    'password': '你的密码',
    'database': 'amazon_sp'
}

# 初始化
config_manager = MultiStoreConfig()
db_manager = create_mysql_manager_from_config(mysql_config)
service = ReportProcessingService(db_manager)

# 获取所有店铺
stores = config_manager.get_all_stores()

# 处理销售报告（最近7天）
print("开始处理销售报告...")
results = service.process_all_stores_sales(stores, days_ago=7)

for result in results:
    if result['success']:
        print(f"✅ {result['store_name']}: {result['records_by_date']} 条记录")
    else:
        print(f"❌ {result['store_name']}: {result['error']}")
```

## 📊 查询数据示例

### 查询最近7天的销售数据

```sql
SELECT 
    s.store_name,
    sr.report_date,
    sr.units_ordered,
    sr.ordered_product_sales,
    sr.page_views,
    sr.sessions,
    sr.buy_box_percentage
FROM sales_reports sr
JOIN stores s ON sr.store_id = s.store_id
WHERE sr.report_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
ORDER BY sr.report_date DESC, s.store_name;
```

### 查询Top 10畅销商品

```sql
SELECT 
    parent_asin,
    SUM(units_ordered) as total_units,
    SUM(ordered_product_sales) as total_sales,
    AVG(buy_box_percentage) as avg_buy_box_pct
FROM sales_reports_by_asin
WHERE report_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY parent_asin
ORDER BY total_units DESC
LIMIT 10;
```

### 查询库存状况

```sql
SELECT 
    s.store_name,
    ir.asin,
    ir.sellable_on_hand_inventory_units,
    ir.unsellable_on_hand_inventory_units,
    ir.sell_through_rate
FROM inventory_reports_by_asin ir
JOIN stores s ON ir.store_id = s.store_id
WHERE ir.report_end_date = (
    SELECT MAX(report_end_date) FROM inventory_reports_by_asin
)
ORDER BY ir.sellable_on_hand_inventory_units DESC;
```

## 🔧 维护建议

### 1. 定期备份数据库

```bash
# 备份
mysqldump -u amazon_user -p amazon_sp > backup_$(date +%Y%m%d).sql

# 恢复
mysql -u amazon_user -p amazon_sp < backup_20250107.sql
```

### 2. 清理历史数据

```sql
-- 删除6个月前的数据
DELETE FROM sales_reports WHERE report_date < DATE_SUB(CURDATE(), INTERVAL 6 MONTH);
DELETE FROM sales_reports_by_asin WHERE report_date < DATE_SUB(CURDATE(), INTERVAL 6 MONTH);
DELETE FROM inventory_reports WHERE report_end_date < DATE_SUB(CURDATE(), INTERVAL 6 MONTH);
```

### 3. 优化数据库

```sql
-- 优化表
OPTIMIZE TABLE sales_reports;
OPTIMIZE TABLE sales_reports_by_asin;
OPTIMIZE TABLE inventory_reports;
OPTIMIZE TABLE inventory_reports_by_asin;

-- 分析表
ANALYZE TABLE sales_reports;
```

## ⚠️ 注意事项

1. **API限流**: Reports API有请求频率限制，建议每天执行1-2次
2. **数据延迟**: 亚马逊报告通常有24-48小时的数据延迟
3. **存储空间**: 长期存储需要足够的磁盘空间
4. **索引优化**: 根据查询需求创建合适的索引
5. **连接池**: 高并发场景建议调整数据库连接池大小

## 🎉 完成

现在您已经成功配置了MySQL数据库并接入了Reports API！

系统会自动：
- ✅ 定时获取销售和库存报告
- ✅ 解析JSON数据
- ✅ 存入MySQL数据库
- ✅ 支持批量查询和分析

---

**版本**: 1.0.0  
**更新时间**: 2025-10-07