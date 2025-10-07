# 🚀 快速开始指南

欢迎使用亚马逊SP API配置管理系统！按照以下步骤，5分钟内即可开始使用。

## 📋 前置要求

- Python 3.7 或更高版本
- pip (Python包管理器)
- 亚马逊卖家账号
- 亚马逊开发者账号（用于获取API凭证）

## ⚡ 快速启动

### 方式1：使用启动脚本（推荐）

#### Linux/Mac用户：
```bash
cd amazon_sp_analytics
./start.sh
```

#### Windows用户：
```bash
cd amazon_sp_analytics
start.bat
```

### 方式2：手动启动

```bash
cd amazon_sp_analytics

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

## 🌐 访问控制台

服务启动后，在浏览器中打开：

```
http://localhost:8000
```

您将看到一个漂亮的配置管理界面！

## 📝 第一次使用

### 步骤1：添加您的第一个店铺

1. 点击 **"➕ 添加店铺"** 标签页
2. 填写以下信息：
   - **店铺ID**: 给店铺取个唯一的ID，例如 `my_store_001`
   - **店铺名称**: 便于识别的名称，例如 `我的美国店铺`
   - **Client ID**: 从亚马逊开发者控制台获取
   - **Client Secret**: 从亚马逊开发者控制台获取
   - **Refresh Token**: 通过OAuth流程获取
   - **区域**: 选择您店铺所在的区域（NA/EU/FE）
   - **Marketplace IDs**: (可选) 例如 `ATVPDKIKX0DER` (美国)

3. 点击 **"✅ 保存配置"**

### 步骤2：测试配置

在保存前，您可以先测试配置是否正确：

1. 点击 **"🔍 测试配置"** 标签页
2. 输入您的API凭证
3. 点击 **"🔍 测试配置"** 按钮
4. 如果看到 ✅ 表示配置正确

### 步骤3：查看和管理店铺

1. 点击 **"📋 店铺列表"** 标签页
2. 查看所有已配置的店铺
3. 可以编辑或删除现有店铺

## 🔑 如何获取API凭证？

### Client ID 和 Client Secret

1. 访问 [Amazon Developer Console](https://developer.amazon.com/)
2. 登录您的开发者账号
3. 创建一个新的 "Login with Amazon" 应用
4. 在应用详情中找到 Client ID 和 Client Secret

### Refresh Token

获取Refresh Token需要通过OAuth授权流程：

1. 在卖家中心注册您的应用
2. 使用OAuth 2.0流程获取授权码
3. 用授权码交换Refresh Token

详细步骤请参考：
- [亚马逊SP API官方文档](https://developer-docs.amazon.com/sp-api/docs)
- [SP API认证指南](https://developer-docs.amazon.com/sp-api/docs/sp-api-registration)

## 📊 Marketplace ID参考

### 北美
- 🇺🇸 美国: `ATVPDKIKX0DER`
- 🇨🇦 加拿大: `A2EUQ1WTGCTBG2`
- 🇲🇽 墨西哥: `A1AM78C64UM0Y8`

### 欧洲
- 🇬🇧 英国: `A1F83G8C2ARO7P`
- 🇩🇪 德国: `A1PA6795UKMFR9`
- 🇫🇷 法国: `A13V1IB3VIYZZH`
- 🇮🇹 意大利: `APJ6JRA9NG5V4`
- 🇪🇸 西班牙: `A1RKKUPIHCS9HS`

### 远东
- 🇯🇵 日本: `A1VC38T7YXB528`
- 🇦🇺 澳大利亚: `A39IBJ37TRP1C6`
- 🇸🇬 新加坡: `A19VAU5U5O7RUS`

## 🎯 常用功能

### 编辑店铺配置

1. 在店铺列表中找到要编辑的店铺
2. 点击 **"✏️ 编辑"** 按钮
3. 修改需要更新的字段
4. 点击 **"保存"**

### 删除店铺配置

1. 在店铺列表中找到要删除的店铺
2. 点击 **"🗑️ 删除"** 按钮
3. 确认删除操作

### 查看API文档

访问 `http://localhost:8000/docs` 查看完整的API文档

## 📁 配置文件位置

所有配置会自动保存在：
```
amazon_sp_analytics/stores_config.yaml
```

建议定期备份此文件！

## 🆘 遇到问题？

### 问题1: 启动失败
- 确认Python版本 >= 3.7
- 检查是否安装了所有依赖：`pip install -r requirements.txt`
- 查看控制台错误信息

### 问题2: 配置测试失败
- 检查Client ID、Client Secret是否正确
- 确认Refresh Token未过期
- 验证区域选择是否正确

### 问题3: 无法访问控制台
- 确认服务已启动
- 检查端口8000是否被占用
- 尝试访问 `http://127.0.0.1:8000`

## 📞 获取帮助

- 查看完整文档：`README.md`
- 查看示例配置：`stores_config.example.yaml`
- 访问API文档：`http://localhost:8000/docs`

## 🎉 开始使用

现在您已经准备好了！享受使用亚马逊SP API配置管理系统吧！

---

**提示**: 第一次使用建议先用沙箱环境（SANDBOX）测试，确认一切正常后再使用生产凭证。