# 🚀 部署指南

## 📦 一、复制项目文件夹

将整个 `amazon_sp_analytics` 文件夹复制到您的服务器：

```bash
# 方式1: 使用scp复制
scp -r amazon_sp_analytics user@your-server:/path/to/

# 方式2: 打包后传输
tar -czf amazon_sp_analytics.tar.gz amazon_sp_analytics/
scp amazon_sp_analytics.tar.gz user@your-server:/path/to/
# 在服务器上解压
tar -xzf amazon_sp_analytics.tar.gz
```

## 💻 二、服务器环境准备

### 1. 安装MySQL

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install mysql-server

# CentOS/RHEL
sudo yum install mysql-server

# 启动MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# 创建数据库
mysql -u root -p
```

MySQL中执行：
```sql
CREATE DATABASE sp_analytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sp_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON sp_analytics.* TO 'sp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2. 安装Python 3.8+

```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip

# 验证版本
python3 --version
```

### 3. 安装Redis（可选，提升性能）

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

## ⚙️ 三、配置系统

### 1. 进入项目目录

```bash
cd amazon_sp_analytics
```

### 2. 运行自动部署脚本

```bash
chmod +x deploy.sh
./deploy.sh
```

脚本会自动：
- 创建Python虚拟环境
- 安装所有依赖
- 创建必要的目录
- 生成配置文件模板

### 3. 配置数据库连接

编辑 `.env` 文件：

```bash
nano .env
```

修改数据库连接：
```bash
DATABASE_URL=mysql+pymysql://sp_user:your_strong_password@localhost/sp_analytics?charset=utf8mb4
```

### 4. 配置店铺信息

编辑 `config.yaml` 文件：

```bash
nano config.yaml
```

填入您的SP API凭证：

```yaml
stores:
  - store_id: store_001
    store_name: 美国主店铺
    client_id: amzn1.application-oa2-client.你的ClientID
    client_secret: 你的ClientSecret
    refresh_token: Atzr|IwEBI你的RefreshToken
    region: NA
    marketplace_ids:
      - ATVPDKIKX0DER
    enabled: true
  
  # 添加更多店铺...
  - store_id: store_002
    store_name: 欧洲店铺
    # ... 继续添加
```

### 5. 初始化数据库

```bash
source venv/bin/activate  # 激活虚拟环境
python3 scripts/init_database.py
```

## 🏃 四、启动服务

### 开发环境启动

```bash
chmod +x start.sh
./start.sh
```

### 生产环境启动（使用Supervisor）

1. 安装Supervisor：

```bash
sudo apt-get install supervisor
```

2. 创建Supervisor配置：

```bash
sudo nano /etc/supervisor/conf.d/sp_analytics.conf
```

内容：
```ini
[program:sp_analytics]
directory=/path/to/amazon_sp_analytics
command=/path/to/amazon_sp_analytics/venv/bin/python main.py
user=your_user
autostart=true
autorestart=true
stderr_logfile=/var/log/sp_analytics.err.log
stdout_logfile=/var/log/sp_analytics.out.log
environment=PATH="/path/to/amazon_sp_analytics/venv/bin"
```

3. 启动服务：

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start sp_analytics
```

查看状态：
```bash
sudo supervisorctl status sp_analytics
```

### 生产环境启动（使用Systemd）

1. 创建服务文件：

```bash
sudo nano /etc/systemd/system/sp-analytics.service
```

内容：
```ini
[Unit]
Description=Amazon SP API Analytics System
After=network.target mysql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/amazon_sp_analytics
Environment="PATH=/path/to/amazon_sp_analytics/venv/bin"
ExecStart=/path/to/amazon_sp_analytics/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. 启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start sp-analytics
sudo systemctl enable sp-analytics  # 开机自启
```

查看状态：
```bash
sudo systemctl status sp-analytics
```

查看日志：
```bash
sudo journalctl -u sp-analytics -f
```

## 🌐 五、配置Nginx反向代理（可选）

### 1. 安装Nginx

```bash
sudo apt-get install nginx
```

### 2. 配置Nginx

```bash
sudo nano /etc/nginx/sites-available/sp-analytics
```

内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/amazon_sp_analytics/static/;
        expires 30d;
    }
}
```

### 3. 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/sp-analytics /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl reload nginx
```

### 4. 配置HTTPS（推荐）

使用Let's Encrypt免费SSL证书：

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🔍 六、验证部署

### 1. 检查服务状态

```bash
# 访问健康检查接口
curl http://localhost:8000/health
```

应返回：
```json
{
  "status": "healthy",
  "timestamp": "2024-10-07T...",
  "version": "1.0.0"
}
```

### 2. 访问Web界面

打开浏览器访问：
- 本地：http://localhost:8000
- 远程：http://your-domain.com

### 3. 测试API

```bash
# 获取实时数据
curl http://localhost:8000/api/v1/realtime/overview

# 获取店铺列表
curl http://localhost:8000/api/v1/stores
```

## 📊 七、监控和维护

### 1. 查看日志

```bash
# 应用日志
tail -f logs/app_*.log

# 系统日志（Systemd）
sudo journalctl -u sp-analytics -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
```

### 2. 数据库维护

```bash
# 备份数据库
mysqldump -u sp_user -p sp_analytics > backup_$(date +%Y%m%d).sql

# 优化表
mysql -u sp_user -p sp_analytics -e "OPTIMIZE TABLE orders_2024_01;"
```

### 3. 性能监控

```bash
# 查看系统资源
top
htop

# 查看MySQL性能
mysql -u sp_user -p -e "SHOW PROCESSLIST;"

# 查看Redis状态（如果使用）
redis-cli info stats
```

## 🔧 八、故障排除

### 问题1：端口被占用

```bash
# 查找占用进程
sudo lsof -i :8000

# 杀死进程
sudo kill -9 <PID>

# 或修改.env中的PORT
PORT=8080
```

### 问题2：数据库连接失败

```bash
# 检查MySQL状态
sudo systemctl status mysql

# 测试连接
mysql -u sp_user -p -h localhost sp_analytics

# 检查防火墙
sudo ufw status
sudo ufw allow 3306/tcp
```

### 问题3：内存不足

```bash
# 查看内存使用
free -h

# 添加交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 问题4：SP API认证失败

- 检查config.yaml中的凭证是否正确
- 确认refresh_token未过期
- 验证region设置正确
- 查看日志获取详细错误信息

## 📈 九、性能优化

### 1. MySQL优化

编辑 `/etc/mysql/my.cnf`：

```ini
[mysqld]
innodb_buffer_pool_size = 2G  # 根据服务器内存调整
max_connections = 200
query_cache_size = 64M
```

### 2. Redis缓存

确保Redis正常运行并在.env中配置：

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3. 增加工作进程

修改main.py中的uvicorn配置：

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    workers=4,  # 增加工作进程
    log_level="info"
)
```

## 🔐 十、安全建议

1. **限制数据库访问**
   ```sql
   -- 只允许本地访问
   GRANT ALL PRIVILEGES ON sp_analytics.* TO 'sp_user'@'localhost';
   ```

2. **配置防火墙**
   ```bash
   sudo ufw enable
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   ```

3. **定期更新**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   ```

4. **备份策略**
   - 每日自动备份数据库
   - 保留最近30天的备份
   - 定期测试恢复流程

## ✅ 部署检查清单

- [ ] MySQL已安装并配置
- [ ] Python 3.8+已安装
- [ ] 虚拟环境已创建
- [ ] 所有依赖已安装
- [ ] .env文件已配置
- [ ] config.yaml已填写SP API凭证
- [ ] 数据库已初始化
- [ ] 服务可以正常启动
- [ ] Web界面可以访问
- [ ] API接口正常响应
- [ ] 日志正常输出
- [ ] 定时任务已配置（如需要）
- [ ] 备份策略已设置
- [ ] 监控已配置
- [ ] Nginx反向代理已配置（如需要）
- [ ] SSL证书已配置（如需要）

---

**恭喜！您已成功部署亚马逊SP API多店铺销售分析系统！** 🎉