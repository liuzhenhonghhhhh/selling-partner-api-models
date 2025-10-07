"""
MySQL数据库管理器
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

from .mysql_models import Base, Store, SalesReport, SalesReportByASIN, InventoryReport, InventoryReportByASIN, ReportRequest

logger = logging.getLogger(__name__)


class MySQLManager:
    """MySQL数据库管理器"""
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        初始化MySQL数据库管理器
        
        Args:
            database_url: 数据库连接URL
                格式: mysql+pymysql://user:password@host:port/database?charset=utf8mb4
            echo: 是否打印SQL语句
        """
        self.database_url = database_url
        
        # 创建数据库引擎
        self.engine = create_engine(
            database_url,
            echo=echo,
            poolclass=QueuePool,
            pool_size=10,
            pool_recycle=3600,
            pool_pre_ping=True,  # 自动检测连接是否可用
            connect_args={
                'charset': 'utf8mb4'
            }
        )
        
        # 创建会话工厂
        self.SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )
        
        logger.info(f"MySQL数据库管理器初始化成功: {database_url.split('@')[-1]}")
    
    def create_all_tables(self):
        """创建所有数据表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    def drop_all_tables(self):
        """删除所有数据表（谨慎使用）"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("所有数据库表已删除")
        except Exception as e:
            logger.error(f"删除数据库表失败: {e}")
            raise
    
    def get_session(self):
        """
        获取数据库会话
        
        Returns:
            Session对象
        """
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """
        提供事务性会话上下文管理器
        
        使用示例:
            with db_manager.session_scope() as session:
                session.add(obj)
                session.commit()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """关闭数据库连接"""
        self.SessionLocal.remove()
        self.engine.dispose()
        logger.info("数据库连接已关闭")
    
    # ========== 便捷方法 ==========
    
    def upsert_store(self, store_data: dict):
        """
        插入或更新店铺信息
        
        Args:
            store_data: 店铺数据字典
        
        Returns:
            Store对象
        """
        with self.session_scope() as session:
            store = session.query(Store).filter_by(store_id=store_data['store_id']).first()
            
            if store:
                # 更新
                for key, value in store_data.items():
                    setattr(store, key, value)
                logger.info(f"店铺信息已更新: {store_data['store_id']}")
            else:
                # 插入
                store = Store(**store_data)
                session.add(store)
                logger.info(f"店铺信息已插入: {store_data['store_id']}")
            
            session.flush()
            session.refresh(store)
            return store
    
    def get_store(self, store_id: str):
        """
        获取店铺信息
        
        Args:
            store_id: 店铺ID
        
        Returns:
            Store对象或None
        """
        with self.session_scope() as session:
            return session.query(Store).filter_by(store_id=store_id).first()
    
    def get_all_stores(self, enabled_only: bool = True):
        """
        获取所有店铺
        
        Args:
            enabled_only: 仅返回启用的店铺
        
        Returns:
            Store对象列表
        """
        with self.session_scope() as session:
            query = session.query(Store)
            if enabled_only:
                query = query.filter_by(enabled=True)
            return query.all()
    
    def bulk_insert_sales_reports(self, reports: list):
        """
        批量插入销售报告
        
        Args:
            reports: SalesReport对象列表
        """
        with self.session_scope() as session:
            session.bulk_save_objects(reports)
            logger.info(f"批量插入 {len(reports)} 条销售报告")
    
    def bulk_insert_inventory_reports(self, reports: list):
        """
        批量插入库存报告
        
        Args:
            reports: InventoryReport对象列表
        """
        with self.session_scope() as session:
            session.bulk_save_objects(reports)
            logger.info(f"批量插入 {len(reports)} 条库存报告")
    
    def update_report_request(self, report_id: str, update_data: dict):
        """
        更新报告请求状态
        
        Args:
            report_id: 报告ID
            update_data: 更新数据字典
        """
        with self.session_scope() as session:
            report = session.query(ReportRequest).filter_by(report_id=report_id).first()
            if report:
                for key, value in update_data.items():
                    setattr(report, key, value)
                logger.info(f"报告请求已更新: {report_id}")
    
    def get_pending_reports(self, limit: int = 100):
        """
        获取待处理的报告请求
        
        Args:
            limit: 返回数量限制
        
        Returns:
            ReportRequest对象列表
        """
        with self.session_scope() as session:
            return session.query(ReportRequest).filter(
                ReportRequest.status.in_(['IN_QUEUE', 'IN_PROGRESS'])
            ).limit(limit).all()


def create_mysql_manager_from_config(config: dict) -> MySQLManager:
    """
    从配置创建MySQL管理器
    
    Args:
        config: 配置字典，包含以下键:
            - host: 主机地址
            - port: 端口
            - user: 用户名
            - password: 密码
            - database: 数据库名
            - charset: 字符集(默认utf8mb4)
    
    Returns:
        MySQLManager实例
    """
    host = config.get('host', 'localhost')
    port = config.get('port', 3306)
    user = config.get('user', 'root')
    password = config.get('password', '')
    database = config.get('database', 'amazon_sp')
    charset = config.get('charset', 'utf8mb4')
    
    database_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
    
    manager = MySQLManager(database_url, echo=config.get('echo', False))
    
    # 自动创建表
    if config.get('auto_create_tables', True):
        manager.create_all_tables()
    
    return manager