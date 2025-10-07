# 安装指南

## 📋 系统要求

- **Python**: 3.6 或更高版本
- **操作系统**: Windows / Linux / macOS
- **Redis** (可选): 用于数据缓存

## 🔧 安装步骤

### 1. 克隆或下载项目

```bash
cd /workspace
# 项目已在 sp_api_analytics 目录中
```

### 2. 安装Python依赖

```bash
cd sp_api_analytics
pip install -r requirements.txt
```

如果遇到依赖冲突，可以使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装Redis (可选)

#### Windows:
下载并安装 [Redis for Windows](https://github.com/microsoftarchive/redis/releases)

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### macOS:
```bash
brew install redis
brew services start redis
```

#### 验证Redis安装:
```bash
redis-cli ping
# 应该返回: PONG
```

### 4. 配置店铺信息

首次运行会自动生成配置模板：

```bash
python main.py
```

或手动创建配置文件：

```bash
python -c "from config.sp_api_config import create_sample_config; create_sample_config('stores_config.yaml')"
```

编辑 `stores_config.yaml`，填入您的SP API凭证：

```yaml
stores:
  - store_id: my_store_001
    store_name: 我的店铺
    client_id: your_actual_client_id
    client_secret: your_actual_client_secret
    refresh_token: your_actual_refresh_token
    region: NA  # 或 EU, FE
    marketplace_ids:
      - ATVPDKIKX0DER  # 美国市场
    enabled: true
```

### 5. 获取SP API凭证

#### 5.1 注册开发者账号
访问 [Amazon Seller Central](https://sellercentral.amazon.com/) 注册开发者账号

#### 5.2 创建应用
1. 登录Seller Central
2. 进入 "开发者中心" > "添加新应用"
3. 填写应用信息
4. 获取 `Client ID` 和 `Client Secret`

#### 5.3 获取刷新令牌
1. 授权您的应用访问店铺数据
2. 获取 `Refresh Token`

详细步骤参考: [SP API官方文档](https://developer-docs.amazon.com/sp-api/docs/registering-your-application)

### 6. 测试安装

运行测试脚本：

```bash
python -c "from config import SPAPIConfig; print('配置加载成功')"
python -c "from core import SPAPIClient; print('客户端模块加载成功')"
python -c "from analytics import OrdersAnalytics; print('分析模块加载成功')"
```

### 7. 运行主程序

```bash
python main.py
```

## 🔍 故障排除

### 问题1: 依赖安装失败

**错误**: `pip install` 失败

**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2: Redis连接失败

**错误**: `Redis连接失败`

**解决方案**:
1. 检查Redis是否运行: `redis-cli ping`
2. 修改配置文件中的Redis地址
3. 或禁用Redis缓存（系统会自动使用内存缓存）

### 问题3: API认证失败

**错误**: `401 Unauthorized` 或 `403 Forbidden`

**解决方案**:
1. 检查 `client_id` 和 `client_secret` 是否正确
2. 确认 `refresh_token` 未过期
3. 验证应用是否已被授权访问店铺数据
4. 检查区域 (region) 设置是否正确

### 问题4: 导入模块失败

**错误**: `ModuleNotFoundError`

**解决方案**:
```bash
# 确保在项目根目录运行
cd /workspace/sp_api_analytics

# 设置PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/workspace/sp_api_analytics"

# Windows:
set PYTHONPATH=%PYTHONPATH%;C:\path\to\sp_api_analytics
```

### 问题5: API限流

**错误**: `429 Too Many Requests`

**解决方案**:
- 系统已内置限流器，会自动遵守速率限制
- 如果频繁遇到此错误，可以增加 `update_interval` 时间
- 启用缓存减少API调用

## 📦 可选组件

### 数据库支持 (可选)

如需持久化存储，可以安装数据库：

```bash
# SQLite (默认，无需额外安装)

# PostgreSQL
pip install psycopg2-binary
# 修改配置: database_url: 'postgresql://user:password@localhost/dbname'

# MySQL
pip install pymysql
# 修改配置: database_url: 'mysql+pymysql://user:password@localhost/dbname'
```

### 异步支持 (高级)

对于100+店铺，建议启用异步支持：

```bash
pip install aiohttp
pip install asyncio
```

### 监控和告警 (可选)

```bash
# 邮件告警
pip install sendgrid

# 短信告警
pip install twilio

# 企业微信/钉钉告警
pip install requests
```

## ✅ 验证安装

运行完整测试：

```bash
# 查看帮助
python main.py --help

# 测试配置
python -c "from config import MultiStoreConfig; config = MultiStoreConfig(); print(f'加载了 {len(config.stores)} 个店铺')"

# 测试Redis
python -c "from cache import init_cache; cache = init_cache(); print('Redis连接成功' if cache.client else '使用内存缓存')"
```

## 🚀 快速开始

安装完成后，查看：
- [README.md](README.md) - 使用说明
- [examples/basic_usage.py](examples/basic_usage.py) - 基础示例
- [examples/multi_store_example.py](examples/multi_store_example.py) - 多店铺示例

## 📞 获取帮助

遇到问题？
1. 查看 [README.md](README.md) 文档
2. 查看 [FEATURES.md](FEATURES.md) 功能说明
3. 提交 GitHub Issue
4. 联系技术支持

---

**提示**: 首次使用建议先使用沙箱环境测试 (`region: SANDBOX`)