# 🚀 快速开始指南

## 一、直接复制部署（推荐）

### 1. 复制整个文件夹

```bash
# 将amazon_sp_analytics文件夹复制到您的服务器
cp -r amazon_sp_analytics /path/to/your/server/
```

### 2. 准备MySQL数据库

```bash
# 创建数据库
mysql -u root -p
```

在MySQL中执行：
```sql
CREATE DATABASE sp_analytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sp_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON sp_analytics.* TO 'sp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 一键部署

```bash
cd amazon_sp_analytics
./deploy.sh
```

### 4. 配置文件

编辑 `.env`:
```bash
DATABASE_URL=mysql+pymysql://sp_user:your_password@localhost/sp_analytics?charset=utf8mb4
```

编辑 `config.yaml`:
```yaml
stores:
  - store_id: store_001
    store_name: 我的店铺
    client_id: amzn1.application-oa2-client.xxxxx
    client_secret: xxxxx
    refresh_token: Atzr|IwEBIxxxxx
    region: NA
    marketplace_ids:
      - ATVPDKIKX0DER
    enabled: true
```

### 5. 启动服务

```bash
./start.sh
```

### 6. 访问界面

打开浏览器: `http://localhost:8000`

## 二、验证部署

### 检查健康状态

```bash
curl http://localhost:8000/health
```

应返回：
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0"
}
```

### 检查API

```bash
# 获取实时数据
curl http://localhost:8000/api/v1/realtime/overview

# 获取店铺列表
curl http://localhost:8000/api/v1/stores
```

## 三、常见问题

### Q: 如何添加更多店铺？

编辑 `config.yaml`，在stores列表中添加：

```yaml
stores:
  - store_id: store_002
    store_name: 新店铺
    # ... 其他配置
```

重启服务即可。

### Q: 数据多久更新一次？

默认每60秒更新一次，可在 `main.py` 中修改：

```python
monitor = RealtimeMonitor(
    multi_store_client=multi_store_client,
    update_interval=60  # 修改这里
)
```

### Q: 如何查看日志？

```bash
tail -f logs/app_*.log
```

### Q: 如何停止服务？

```bash
# 按 Ctrl+C 停止
# 或查找进程并结束
ps aux | grep main.py
kill -9 <PID>
```

## 四、生产环境建议

1. **使用Nginx反向代理**
2. **配置SSL证书**
3. **使用Supervisor/Systemd管理进程**
4. **定期备份数据库**
5. **配置日志轮转**

详见：`DEPLOYMENT_GUIDE.md`

---

**5分钟即可完成部署！** 🎉
