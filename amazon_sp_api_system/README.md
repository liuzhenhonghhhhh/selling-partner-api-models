# 🛒 亚马逊SP API数据分析系统

## 📌 项目简介

这是一个**功能完整**的亚马逊卖家数据分析系统，支持：

✅ **可视化配置管理** - 通过Web界面管理API配置，无需手动编辑文件  
✅ **MySQL数据库** - 高性能存储销售和库存数据  
✅ **Reports API集成** - 批量获取数据（官方推荐方式）  
✅ **自动化调度** - 定时自动更新数据  
✅ **多店铺支持** - 同时管理多个亚马逊店铺  

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置MySQL数据库

```sql
CREATE DATABASE amazon_sp CHARACTER SET utf8mb4;
CREATE USER 'amazon_user'@'localhost' IDENTIFIED BY '你的密码';
GRANT ALL PRIVILEGES ON amazon_sp.* TO 'amazon_user'@'localhost';
FLUSH PRIVILEGES;
```

详细配置请查看: `docs/配置MySQL数据库.md`

### 3. 启动系统

**Linux/Mac**:
```bash
./start.sh
```

**Windows**:
```bash
start.bat
```

**或手动启动**:
```bash
python main.py
```

### 4. 访问Web界面

打开浏览器访问: `http://localhost:8000`

在界面中：
- ➕ 添加店铺配置
- ✏️ 编辑现有配置
- 🔍 测试API凭证
- 📋 查看所有店铺

---

## 📊 核心功能

### 1. 可视化配置管理

- 无需手动编辑配置文件
- 在线添加/编辑/删除店铺
- 测试API凭证有效性
- 实时保存配置

### 2. Reports API批量数据获取

**为什么使用Reports API？**

| 对比项 | 单独API调用 | Reports API |
|--------|------------|------------|
| 效率 | ❌ 低，需多次调用 | ✅ 高，批量获取 |
| API限流 | ❌ 容易触发限制 | ✅ 友好 |
| 数据完整性 | ❌ 可能遗漏 | ✅ 完整 |
| 官方推荐 | ❌ 不推荐 | ✅ 官方推荐 |

**支持的报告**:
- ✅ 销售和流量报告
- ✅ 库存报告
- ✅ 订单报告
- ✅ 财务报告

### 3. MySQL数据库存储

**数据表结构**:
- `stores` - 店铺信息
- `sales_reports` - 销售数据（按日期）
- `sales_reports_by_asin` - 销售数据（按商品）
- `inventory_reports` - 库存数据（汇总）
- `inventory_reports_by_asin` - 库存数据（按商品）
- `report_requests` - 报告请求记录

### 4. 自动化定时调度

设置后自动执行：
- 每天定时获取销售报告
- 每天定时获取库存报告
- 自动下载、解析、存储
- 无需人工干预

---

## 📁 项目结构

```
amazon_sp_api_system/
├── app/                        # 应用核心代码
│   ├── api/                    # API接口
│   │   ├── routes.py          # 路由定义
│   │   └── schemas.py         # 数据模型
│   ├── config/                 # 配置管理
│   │   └── sp_api_config.py   # SP API配置
│   ├── core/                   # 核心功能
│   │   ├── sp_client.py       # SP API基础客户端
│   │   └── reports_client.py  # Reports API客户端
│   ├── models/                 # 数据模型
│   │   ├── mysql_models.py    # MySQL表结构
│   │   └── mysql_manager.py   # MySQL管理器
│   └── services/               # 业务服务
│       ├── report_parser.py   # 报告解析器
│       ├── report_service.py  # 报告处理服务
│       └── report_scheduler.py # 定时调度器
├── static/                     # 静态资源
│   └── config.html            # 配置管理界面
├── docs/                       # 文档
│   ├── 中文使用指南.md        # 完整使用指南
│   ├── 配置MySQL数据库.md     # MySQL配置指南
│   ├── MYSQL_REPORTS_完成说明.md
│   └── 其他文档...
├── examples/                   # 使用示例
│   └── 使用Reports_API示例.py
├── main.py                     # 主程序入口
├── requirements.txt            # Python依赖
├── start.sh                    # Linux/Mac启动脚本
├── start.bat                   # Windows启动脚本
├── stores_config.example.yaml  # 配置示例
└── README.md                   # 本文件
```

---

## 💡 使用示例

### 示例1：使用Web界面（推荐）

1. 启动系统: `python main.py`
2. 访问: `http://localhost:8000`
3. 添加店铺配置
4. 完成！

### 示例2：使用代码

```python
from app.config.sp_api_config import MultiStoreConfig
from app.models.mysql_manager import create_mysql_manager_from_config
from app.services.report_service import ReportProcessingService

# MySQL配置
mysql_config = {
    'host': 'localhost',
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
results = service.process_all_stores_sales(stores, days_ago=7)

# 查看结果
for result in results:
    if result['success']:
        print(f"✅ {result['store_name']}: {result['records_by_date']} 条记录")
```

### 示例3：定时任务

```python
from app.services.report_scheduler import ReportScheduler

scheduler = ReportScheduler(config_manager, db_manager)

# 每天凌晨2点获取销售数据
scheduler.schedule_sales_reports(time_str="02:00", days_ago=1)

# 每天凌晨3点获取库存数据
scheduler.schedule_inventory_reports(time_str="03:00", days_ago=1)

# 启动调度器
scheduler.start()
```

---

## 📖 文档说明

| 文档 | 说明 |
|------|------|
| `中文使用指南.md` | 完整的使用指南（推荐阅读）|
| `配置MySQL数据库.md` | MySQL数据库配置详细步骤 |
| `MYSQL_REPORTS_完成说明.md` | 系统功能完成说明 |
| `开始使用.txt` | 快速参考指南 |

---

## 🔧 系统要求

- Python 3.7+
- MySQL 5.7+ 或 8.0+
- 亚马逊卖家账号
- SP API开发者凭证

---

## 📊 数据查询示例

### 查询最近7天销售数据

```sql
SELECT 
    report_date,
    SUM(units_ordered) as 订单数,
    SUM(ordered_product_sales) as 销售额
FROM sales_reports
WHERE report_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY report_date
ORDER BY report_date;
```

### 查询Top 10商品

```sql
SELECT 
    parent_asin,
    SUM(units_ordered) as 销量,
    SUM(ordered_product_sales) as 销售额
FROM sales_reports_by_asin
WHERE report_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY parent_asin
ORDER BY 销量 DESC
LIMIT 10;
```

---

## ⚠️ 注意事项

1. **API限流**: Reports API有请求频率限制，建议每天执行1-2次
2. **数据延迟**: 销售数据通常有24-48小时延迟
3. **配置安全**: 不要将配置文件提交到公共仓库
4. **定期备份**: 定期备份MySQL数据库

---

## 🆘 常见问题

**Q: 报告生成需要多长时间？**  
A: 通常5-15分钟，系统会自动等待。

**Q: 可以获取实时数据吗？**  
A: Reports API获取的是历史数据，有延迟。

**Q: 如何获取API凭证？**  
A: 访问 Amazon Developer Console 注册应用并授权。

**Q: 支持多个Marketplace吗？**  
A: 支持，可在配置中指定多个Marketplace ID。

---

## 📞 技术支持

查看详细文档：
- `docs/中文使用指南.md`
- `docs/配置MySQL数据库.md`

运行示例代码：
- `examples/使用Reports_API示例.py`

---

## 📝 更新日志

### v1.0.0 (2025-10-07)
- ✅ 初始版本发布
- ✅ 可视化配置管理
- ✅ MySQL数据库集成
- ✅ Reports API批量获取
- ✅ 自动化调度系统
- ✅ 完整中文文档

---

## 📄 许可证

MIT License

---

## 🎉 开始使用

```bash
# 1. 克隆或下载项目
# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动系统
python main.py

# 4. 访问 http://localhost:8000
# 5. 开始配置您的亚马逊店铺！
```

**享受使用！** 🚀