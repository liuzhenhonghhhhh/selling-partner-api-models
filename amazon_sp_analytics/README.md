# 亚马逊SP API配置管理系统

🚀 一个现代化的、可视化的亚马逊卖家API配置管理系统，无需手动编辑配置文件！

## ✨ 特性

- 🎨 **可视化配置管理** - 通过现代化的Web界面轻松管理API配置
- 🏪 **多店铺支持** - 同时管理多个亚马逊卖家店铺
- 🔒 **安全存储** - 配置安全保存在YAML文件中
- 🧪 **配置测试** - 在保存前测试API凭证是否有效
- ⚡ **实时更新** - 配置更改立即生效
- 📱 **响应式设计** - 完美支持桌面和移动设备

## 🛠️ 安装

### 1. 安装依赖

```bash
cd amazon_sp_analytics
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动

## 📖 使用指南

### 访问配置管理控制台

启动服务后，在浏览器中打开：

```
http://localhost:8000
```

您将看到一个美观的配置管理界面，包含三个主要标签页：

#### 1️⃣ 店铺列表

- 查看所有已配置的店铺
- 显示每个店铺的状态、区域、Marketplace等信息
- 可以编辑或删除现有店铺

#### 2️⃣ 添加店铺

填写以下必填信息即可添加新店铺：

- **店铺ID**: 唯一标识符（例如：store_001）
- **店铺名称**: 便于识别的名称（例如：美国主店铺）
- **Client ID**: 从亚马逊开发者控制台获取的LWA应用Client ID
- **Client Secret**: LWA应用的Client Secret
- **Refresh Token**: 卖家授权后获得的刷新令牌
- **区域**: 选择店铺所在区域（NA/EU/FE）
- **Marketplace IDs**: (可选) 市场ID列表，用逗号分隔

**可选的AWS高级配置**：
- AWS Access Key
- AWS Secret Key
- IAM Role ARN

#### 3️⃣ 测试配置

在保存配置前，可以先测试API凭证是否有效：

1. 输入Client ID、Client Secret、Refresh Token和区域
2. 点击"测试配置"
3. 系统会验证凭证是否有效

### API端点

系统提供完整的RESTful API：

#### 配置管理

- `GET /api/config/stores` - 获取所有店铺配置
- `GET /api/config/stores/{store_id}` - 获取指定店铺配置
- `POST /api/config/stores` - 创建新店铺配置
- `PUT /api/config/stores/{store_id}` - 更新店铺配置
- `DELETE /api/config/stores/{store_id}` - 删除店铺配置
- `POST /api/config/test` - 测试API配置

### 查看API文档

访问 `http://localhost:8000/docs` 查看完整的交互式API文档（Swagger UI）

## 🔧 配置文件

配置会自动保存在 `stores_config.yaml` 文件中，格式如下：

```yaml
global:
  redis_host: localhost
  redis_port: 6379
  database_url: sqlite:///sp_api_analytics.db
  log_level: INFO

stores:
  - store_id: store_001
    store_name: 美国主店铺
    client_id: amzn1.application-oa2-client.xxxxx
    client_secret: xxxxx
    refresh_token: Atzr|xxxxx
    region: NA
    marketplace_ids:
      - ATVPDKIKX0DER
    enabled: true
```

## 📊 支持的区域和Marketplace

### 北美 (NA)
- 🇺🇸 美国: ATVPDKIKX0DER
- 🇨🇦 加拿大: A2EUQ1WTGCTBG2
- 🇲🇽 墨西哥: A1AM78C64UM0Y8

### 欧洲 (EU)
- 🇬🇧 英国: A1F83G8C2ARO7P
- 🇩🇪 德国: A1PA6795UKMFR9
- 🇫🇷 法国: A13V1IB3VIYZZH
- 🇮🇹 意大利: APJ6JRA9NG5V4
- 🇪🇸 西班牙: A1RKKUPIHCS9HS

### 远东 (FE)
- 🇯🇵 日本: A1VC38T7YXB528
- 🇦🇺 澳大利亚: A39IBJ37TRP1C6
- 🇸🇬 新加坡: A19VAU5U5O7RUS

## 🔐 获取API凭证

### 步骤1: 注册开发者账号

1. 访问 [Amazon Developer Console](https://developer.amazon.com/)
2. 使用您的亚马逊卖家账号登录
3. 注册为开发者

### 步骤2: 创建LWA应用

1. 在开发者控制台创建新的"Login with Amazon"应用
2. 记录 `Client ID` 和 `Client Secret`

### 步骤3: 获取Refresh Token

1. 在卖家中心授权您的应用
2. 通过OAuth流程获取 `Refresh Token`

详细步骤请参考：[亚马逊SP API官方文档](https://developer-docs.amazon.com/sp-api/docs/sp-api-registration)

## 🎯 常见问题

### Q: 如何知道配置是否正确？

A: 使用"测试配置"标签页验证您的API凭证。

### Q: 可以同时管理多少个店铺？

A: 没有限制，您可以添加任意数量的店铺配置。

### Q: 配置保存在哪里？

A: 配置保存在 `stores_config.yaml` 文件中，您可以备份此文件。

### Q: 如何切换到生产环境？

A: 确保使用生产环境的凭证，并将区域设置为正确的值（不要使用SANDBOX）。

## 🚨 安全建议

1. ⚠️ **不要分享** 您的 Client Secret 和 Refresh Token
2. 🔒 **定期更新** Refresh Token
3. 📁 **备份配置文件** 到安全的地方
4. 🌐 **生产环境** 建议使用HTTPS和访问控制

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 支持

如有问题，请创建Issue或联系开发团队。

---

**享受使用亚马逊SP API配置管理系统！** 🎉