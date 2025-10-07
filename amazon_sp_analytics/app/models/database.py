"""
数据库模型设计
采用年份+月份分表策略（如：orders_2024_01, orders_2024_02）
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Index, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class Store(Base):
    """店铺信息表"""
    __tablename__ = 'stores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(50), unique=True, nullable=False, index=True)
    store_name = Column(String(200), nullable=False)
    region = Column(String(20), nullable=False)
    marketplace_ids = Column(Text)
    client_id = Column(String(200))
    client_secret = Column(String(200))
    refresh_token = Column(Text)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_store_region', 'region'),
        Index('idx_store_enabled', 'enabled'),
    )


class OrderBase(Base):
    """订单数据基础表（按年月分表，如：orders_2024_01）"""
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(50), nullable=False, index=True)
    order_id = Column(String(100), nullable=False, unique=True, index=True)
    marketplace_id = Column(String(50), nullable=False)
    purchase_date = Column(DateTime, nullable=False, index=True)
    last_update_date = Column(DateTime)
    order_status = Column(String(50), index=True)
    fulfillment_channel = Column(String(20))
    sales_channel = Column(String(100))
    
    # 金额信息
    order_total_amount = Column(Float, default=0)
    order_total_currency = Column(String(10))
    
    # 买家信息
    buyer_email = Column(String(200))
    buyer_name = Column(String(200))
    
    # 配送信息
    ship_city = Column(String(100))
    ship_state = Column(String(100))
    ship_country = Column(String(50), index=True)
    ship_postal_code = Column(String(20))
    
    # 商品信息（JSON）
    items = Column(Text)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_store_purchase', 'store_id', 'purchase_date'),
        Index('idx_status_date', 'order_status', 'purchase_date'),
    )


class SalesMetricBase(Base):
    """销售指标表（按年月分表，如：sales_metrics_2024_01）"""
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(50), nullable=False, index=True)
    marketplace_id = Column(String(50), nullable=False)
    
    # 时间维度
    interval_start = Column(DateTime, nullable=False, index=True)
    interval_end = Column(DateTime, nullable=False)
    granularity = Column(String(20))
    
    # 销售指标
    order_count = Column(Integer, default=0)
    unit_count = Column(Integer, default=0)
    total_sales_amount = Column(Float, default=0)
    total_sales_currency = Column(String(10))
    
    # 计算指标
    average_order_value = Column(Float, default=0)
    average_units_per_order = Column(Float, default=0)
    
    buyer_type = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_store_interval', 'store_id', 'interval_start'),
    )


class FinancialEventBase(Base):
    """财务事件表（按年月分表，如：financial_events_2024_01）"""
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(50), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    posted_date = Column(DateTime, nullable=False, index=True)
    
    order_id = Column(String(100), index=True)
    marketplace_id = Column(String(50))
    
    # 财务数据
    revenue_amount = Column(Float, default=0)
    fee_amount = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    currency_code = Column(String(10))
    
    # 详细数据（JSON）
    revenue_breakdown = Column(Text)
    fee_breakdown = Column(Text)
    
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_store_posted', 'store_id', 'posted_date'),
    )


class MonitoringSnapshot(Base):
    """监控快照表"""
    __tablename__ = 'monitoring_snapshots'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    snapshot_time = Column(DateTime, nullable=False, index=True)
    
    total_stores = Column(Integer, default=0)
    total_orders_1h = Column(Integer, default=0)
    total_revenue_1h = Column(Float, default=0)
    total_revenue_24h = Column(Float, default=0)
    total_profit_7d = Column(Float, default=0)
    
    orders_per_hour = Column(Float, default=0)
    revenue_per_hour = Column(Float, default=0)
    average_order_value = Column(Float, default=0)
    average_profit_margin = Column(Float, default=0)
    
    store_metrics = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class Alert(Base):
    """告警记录表"""
    __tablename__ = 'alerts'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_time = Column(DateTime, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20))
    
    message = Column(Text, nullable=False)
    value = Column(Float)
    threshold = Column(Float)
    store_id = Column(String(50), index=True)
    
    status = Column(String(20), default='active')
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.now)


class DailySummary(Base):
    """每日汇总表"""
    __tablename__ = 'daily_summaries'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(50), nullable=False, index=True)
    summary_date = Column(DateTime, nullable=False, index=True)
    
    # 订单指标
    total_orders = Column(Integer, default=0)
    total_units = Column(Integer, default=0)
    total_revenue = Column(Float, default=0)
    average_order_value = Column(Float, default=0)
    
    # 财务指标
    total_fees = Column(Float, default=0)
    total_refunds = Column(Float, default=0)
    net_profit = Column(Float, default=0)
    profit_margin = Column(Float, default=0)
    
    # 订单状态分布（JSON）
    order_status_distribution = Column(Text)
    
    # 渠道分布
    afn_orders = Column(Integer, default=0)
    mfn_orders = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_store_date', 'store_id', 'summary_date'),
        Index('idx_unique_store_date', 'store_id', 'summary_date', unique=True),
    )


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.month_tables = {}
    
    def create_all_tables(self):
        """创建所有基础表"""
        Base.metadata.create_all(self.engine)
    
    def create_month_tables(self, year: int, month: int):
        """
        创建指定年月的分表
        
        Args:
            year: 年份
            month: 月份 (1-12)
        
        Returns:
            包含该月所有表的字典
        """
        month_key = f"{year}_{month:02d}"
        
        if month_key in self.month_tables:
            return self.month_tables[month_key]
        
        # 创建订单表
        OrderTable = type(
            f'Order{year}{month:02d}',
            (OrderBase,),
            {'__tablename__': f'orders_{year}_{month:02d}'}
        )
        
        # 创建销售指标表
        SalesMetricTable = type(
            f'SalesMetric{year}{month:02d}',
            (SalesMetricBase,),
            {'__tablename__': f'sales_metrics_{year}_{month:02d}'}
        )
        
        # 创建财务事件表
        FinancialEventTable = type(
            f'FinancialEvent{year}{month:02d}',
            (FinancialEventBase,),
            {'__tablename__': f'financial_events_{year}_{month:02d}'}
        )
        
        # 创建表
        OrderTable.__table__.create(self.engine, checkfirst=True)
        SalesMetricTable.__table__.create(self.engine, checkfirst=True)
        FinancialEventTable.__table__.create(self.engine, checkfirst=True)
        
        self.month_tables[month_key] = {
            'orders': OrderTable,
            'sales_metrics': SalesMetricTable,
            'financial_events': FinancialEventTable
        }
        
        return self.month_tables[month_key]
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def get_month_table(self, table_type: str, year: int, month: int):
        """
        获取指定年月的表
        
        Args:
            table_type: 表类型 (orders, sales_metrics, financial_events)
            year: 年份
            month: 月份
        
        Returns:
            表类
        """
        month_key = f"{year}_{month:02d}"
        
        if month_key not in self.month_tables:
            self.create_month_tables(year, month)
        
        return self.month_tables[month_key].get(table_type)
    
    def auto_create_tables_for_date_range(self, start_date: datetime, end_date: datetime):
        """
        自动创建日期范围内所有月份的表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        current = start_date
        while current <= end_date:
            self.create_month_tables(current.year, current.month)
            
            # 移到下个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)


if __name__ == "__main__":
    # 测试
    db_manager = DatabaseManager("mysql+pymysql://root:password@localhost/sp_analytics?charset=utf8mb4")
    db_manager.create_all_tables()
    
    # 创建2024年1-12月的表
    for month in range(1, 13):
        db_manager.create_month_tables(2024, month)
    
    print("数据库表创建成功！")