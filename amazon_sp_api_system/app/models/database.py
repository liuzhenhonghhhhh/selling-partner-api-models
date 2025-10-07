"""
数据库模型设计
采用按年份分表策略，优化查询性能
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, Index
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
    region = Column(String(20), nullable=False)  # NA, EU, FE
    marketplace_ids = Column(Text)  # JSON array
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
    """订单数据基础表（按年份分表）"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(50), nullable=False, index=True)
    order_id = Column(String(100), nullable=False, index=True)
    marketplace_id = Column(String(50), nullable=False)
    purchase_date = Column(DateTime, nullable=False, index=True)
    last_update_date = Column(DateTime)
    order_status = Column(String(50), index=True)
    fulfillment_channel = Column(String(20))  # AFN, MFN
    sales_channel = Column(String(100))
    order_type = Column(String(50))
    
    # 订单金额
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
    items = Column(Text)  # JSON array of order items
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        Index('idx_store_purchase', 'store_id', 'purchase_date'),
        Index('idx_status_date', 'order_status', 'purchase_date'),
    )


class SalesMetricBase(Base):
    """销售指标表（按年份分表）"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(50), nullable=False, index=True)
    marketplace_id = Column(String(50), nullable=False)
    
    # 时间维度
    interval_start = Column(DateTime, nullable=False, index=True)
    interval_end = Column(DateTime, nullable=False)
    granularity = Column(String(20))  # Hour, Day, Week, Month
    
    # 销售指标
    order_count = Column(Integer, default=0)
    unit_count = Column(Integer, default=0)
    total_sales_amount = Column(Float, default=0)
    total_sales_currency = Column(String(10))
    
    # 计算指标
    average_order_value = Column(Float, default=0)
    average_units_per_order = Column(Float, default=0)
    
    # 买家类型
    buyer_type = Column(String(20))  # B2B, B2C, All
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_store_interval', 'store_id', 'interval_start'),
        Index('idx_granularity_date', 'granularity', 'interval_start'),
    )


class FinancialEventBase(Base):
    """财务事件表（按年份分表）"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(50), nullable=False, index=True)
    
    # 事件信息
    event_type = Column(String(50), nullable=False, index=True)  # Shipment, Refund, Adjustment
    posted_date = Column(DateTime, nullable=False, index=True)
    
    # 关联订单
    order_id = Column(String(100), index=True)
    marketplace_id = Column(String(50))
    
    # 财务数据
    revenue_amount = Column(Float, default=0)
    fee_amount = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    currency_code = Column(String(10))
    
    # 详细数据（JSON）
    revenue_breakdown = Column(Text)  # JSON object
    fee_breakdown = Column(Text)  # JSON object
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_store_posted', 'store_id', 'posted_date'),
        Index('idx_type_date', 'event_type', 'posted_date'),
    )


class MonitoringSnapshot(Base):
    """监控快照表"""
    __tablename__ = 'monitoring_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_time = Column(DateTime, nullable=False, index=True)
    
    # 汇总指标
    total_stores = Column(Integer, default=0)
    total_orders_1h = Column(Integer, default=0)
    total_revenue_1h = Column(Float, default=0)
    total_revenue_24h = Column(Float, default=0)
    total_profit_7d = Column(Float, default=0)
    
    # 速率指标
    orders_per_hour = Column(Float, default=0)
    revenue_per_hour = Column(Float, default=0)
    average_order_value = Column(Float, default=0)
    average_profit_margin = Column(Float, default=0)
    
    # 详细数据（JSON）
    store_metrics = Column(Text)  # JSON array
    
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_snapshot_time', 'snapshot_time'),
    )


class Alert(Base):
    """告警记录表"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_time = Column(DateTime, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20))  # info, warning, critical
    
    # 告警内容
    message = Column(Text, nullable=False)
    value = Column(Float)
    threshold = Column(Float)
    
    # 关联店铺
    store_id = Column(String(50), index=True)
    
    # 状态
    status = Column(String(20), default='active')  # active, acknowledged, resolved
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_alert_status', 'status', 'alert_time'),
        Index('idx_alert_type_time', 'alert_type', 'alert_time'),
    )


class DailySummary(Base):
    """每日汇总表"""
    __tablename__ = 'daily_summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
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
    
    __table_args__ = (
        Index('idx_store_date', 'store_id', 'summary_date'),
    )


def create_year_table(base_class, year: int):
    """动态创建年份表"""
    table_name = f"{base_class.__tablename__}_{year}"
    
    class YearTable(base_class):
        __tablename__ = table_name
    
    return YearTable


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
        self.year_tables = {}
    
    def create_all_tables(self):
        """创建所有基础表"""
        Base.metadata.create_all(self.engine)
    
    def create_year_tables(self, year: int):
        """创建指定年份的分表"""
        if year in self.year_tables:
            return self.year_tables[year]
        
        # 创建订单表
        OrderTable = type(
            f'Order{year}',
            (OrderBase,),
            {'__tablename__': f'orders_{year}'}
        )
        
        # 创建销售指标表
        SalesMetricTable = type(
            f'SalesMetric{year}',
            (SalesMetricBase,),
            {'__tablename__': f'sales_metrics_{year}'}
        )
        
        # 创建财务事件表
        FinancialEventTable = type(
            f'FinancialEvent{year}',
            (FinancialEventBase,),
            {'__tablename__': f'financial_events_{year}'}
        )
        
        # 创建表
        OrderTable.__table__.create(self.engine, checkfirst=True)
        SalesMetricTable.__table__.create(self.engine, checkfirst=True)
        FinancialEventTable.__table__.create(self.engine, checkfirst=True)
        
        self.year_tables[year] = {
            'orders': OrderTable,
            'sales_metrics': SalesMetricTable,
            'financial_events': FinancialEventTable
        }
        
        return self.year_tables[year]
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def get_year_table(self, table_type: str, year: int):
        """获取指定年份的表"""
        if year not in self.year_tables:
            self.create_year_tables(year)
        return self.year_tables[year].get(table_type)


if __name__ == "__main__":
    # 测试数据库连接
    db_manager = DatabaseManager("mysql+pymysql://user:password@localhost/sp_analytics")
    db_manager.create_all_tables()
    
    # 创建2024年的表
    db_manager.create_year_tables(2024)
    
    print("数据库表创建成功！")