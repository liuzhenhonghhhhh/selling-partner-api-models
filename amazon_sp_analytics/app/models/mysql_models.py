"""
MySQL数据库模型
定义销售、订单、库存等数据表结构
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, Index, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Store(Base):
    """店铺表"""
    __tablename__ = 'stores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(100), unique=True, nullable=False, index=True, comment='店铺唯一标识')
    store_name = Column(String(200), nullable=False, comment='店铺名称')
    region = Column(String(20), nullable=False, comment='区域: NA/EU/FE')
    marketplace_ids = Column(JSON, comment='Marketplace ID列表')
    enabled = Column(Boolean, default=True, comment='是否启用')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    sales_reports = relationship('SalesReport', back_populates='store', cascade='all, delete-orphan')
    inventory_reports = relationship('InventoryReport', back_populates='store', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Store(store_id='{self.store_id}', name='{self.store_name}')>"


class SalesReport(Base):
    """销售报告表 - 按日期汇总"""
    __tablename__ = 'sales_reports'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(100), ForeignKey('stores.store_id'), nullable=False, index=True)
    report_date = Column(DateTime, nullable=False, index=True, comment='报告日期')
    marketplace_id = Column(String(50), comment='市场ID')
    
    # 销售数据
    ordered_product_sales = Column(Float, default=0.0, comment='已订购产品销售额')
    ordered_product_sales_b2b = Column(Float, default=0.0, comment='B2B销售额')
    units_ordered = Column(Integer, default=0, comment='订购数量')
    units_ordered_b2b = Column(Integer, default=0, comment='B2B订购数量')
    total_order_items = Column(Integer, default=0, comment='订单项总数')
    total_order_items_b2b = Column(Integer, default=0, comment='B2B订单项总数')
    
    average_sales_per_order_item = Column(Float, default=0.0, comment='每订单项平均销售额')
    average_units_per_order_item = Column(Float, default=0.0, comment='每订单项平均数量')
    average_selling_price = Column(Float, default=0.0, comment='平均售价')
    
    units_refunded = Column(Integer, default=0, comment='退款数量')
    refund_rate = Column(Float, default=0.0, comment='退款率 %')
    
    claims_granted = Column(Integer, default=0, comment='A-to-z索赔数')
    claims_amount = Column(Float, default=0.0, comment='索赔金额')
    
    shipped_product_sales = Column(Float, default=0.0, comment='已发货产品销售额')
    units_shipped = Column(Integer, default=0, comment='已发货数量')
    orders_shipped = Column(Integer, default=0, comment='已发货订单数')
    
    # 流量数据
    browser_page_views = Column(Integer, default=0, comment='浏览器页面浏览量')
    mobile_app_page_views = Column(Integer, default=0, comment='移动端页面浏览量')
    page_views = Column(Integer, default=0, comment='总页面浏览量')
    
    browser_sessions = Column(Integer, default=0, comment='浏览器会话数')
    mobile_app_sessions = Column(Integer, default=0, comment='移动端会话数')
    sessions = Column(Integer, default=0, comment='总会话数')
    
    buy_box_percentage = Column(Float, default=0.0, comment='Buy Box获取率 %')
    order_item_session_percentage = Column(Float, default=0.0, comment='订单项会话转化率 %')
    unit_session_percentage = Column(Float, default=0.0, comment='单位会话转化率 %')
    
    average_offer_count = Column(Integer, default=0, comment='平均Offer数量')
    average_parent_items = Column(Integer, default=0, comment='平均父商品数')
    
    feedback_received = Column(Integer, default=0, comment='收到的反馈数')
    negative_feedback_received = Column(Integer, default=0, comment='收到的负面反馈数')
    received_negative_feedback_rate = Column(Float, default=0.0, comment='负面反馈率 %')
    
    currency_code = Column(String(10), default='USD', comment='货币代码')
    
    created_at = Column(DateTime, default=datetime.utcnow, comment='记录创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='记录更新时间')
    
    # 关系
    store = relationship('Store', back_populates='sales_reports')
    
    # 索引
    __table_args__ = (
        Index('idx_store_date', 'store_id', 'report_date'),
        Index('idx_date', 'report_date'),
    )
    
    def __repr__(self):
        return f"<SalesReport(store='{self.store_id}', date='{self.report_date}')>"


class SalesReportByASIN(Base):
    """销售报告表 - 按ASIN汇总"""
    __tablename__ = 'sales_reports_by_asin'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(100), ForeignKey('stores.store_id'), nullable=False, index=True)
    report_date = Column(DateTime, nullable=False, index=True, comment='报告日期')
    
    parent_asin = Column(String(20), index=True, comment='父ASIN')
    child_asin = Column(String(20), index=True, comment='子ASIN')
    sku = Column(String(100), index=True, comment='SKU')
    
    # 销售数据
    units_ordered = Column(Integer, default=0, comment='订购数量')
    units_ordered_b2b = Column(Integer, default=0, comment='B2B订购数量')
    ordered_product_sales = Column(Float, default=0.0, comment='已订购产品销售额')
    ordered_product_sales_b2b = Column(Float, default=0.0, comment='B2B销售额')
    total_order_items = Column(Integer, default=0, comment='订单项总数')
    total_order_items_b2b = Column(Integer, default=0, comment='B2B订单项总数')
    
    # 流量数据
    browser_sessions = Column(Integer, default=0, comment='浏览器会话数')
    mobile_app_sessions = Column(Integer, default=0, comment='移动端会话数')
    sessions = Column(Integer, default=0, comment='总会话数')
    
    browser_session_percentage = Column(Float, default=0.0, comment='浏览器会话占比 %')
    mobile_app_session_percentage = Column(Float, default=0.0, comment='移动端会话占比 %')
    session_percentage = Column(Float, default=0.0, comment='会话占比 %')
    
    browser_page_views = Column(Integer, default=0, comment='浏览器页面浏览量')
    mobile_app_page_views = Column(Integer, default=0, comment='移动端页面浏览量')
    page_views = Column(Integer, default=0, comment='总页面浏览量')
    
    browser_page_views_percentage = Column(Float, default=0.0, comment='浏览器页面浏览占比 %')
    mobile_app_page_views_percentage = Column(Float, default=0.0, comment='移动端页面浏览占比 %')
    page_views_percentage = Column(Float, default=0.0, comment='页面浏览占比 %')
    
    buy_box_percentage = Column(Float, default=0.0, comment='Buy Box获取率 %')
    unit_session_percentage = Column(Float, default=0.0, comment='单位会话转化率 %')
    
    currency_code = Column(String(10), default='USD', comment='货币代码')
    
    created_at = Column(DateTime, default=datetime.utcnow, comment='记录创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='记录更新时间')
    
    # 索引
    __table_args__ = (
        Index('idx_store_asin_date', 'store_id', 'parent_asin', 'report_date'),
        Index('idx_asin', 'parent_asin'),
        Index('idx_sku', 'sku'),
    )
    
    def __repr__(self):
        return f"<SalesReportByASIN(store='{self.store_id}', asin='{self.parent_asin}')>"


class InventoryReport(Base):
    """库存报告表 - 按日期汇总"""
    __tablename__ = 'inventory_reports'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(100), ForeignKey('stores.store_id'), nullable=False, index=True)
    report_start_date = Column(DateTime, nullable=False, index=True, comment='报告开始日期')
    report_end_date = Column(DateTime, nullable=False, index=True, comment='报告结束日期')
    marketplace_id = Column(String(50), comment='市场ID')
    
    # 库存指标
    vendor_confirmation_rate = Column(Float, default=0.0, comment='供应商确认率')
    net_received_inventory_cost = Column(Float, default=0.0, comment='净收到库存成本')
    net_received_inventory_units = Column(Integer, default=0, comment='净收到库存数量')
    open_purchase_order_units = Column(Integer, default=0, comment='未完成采购订单数量')
    average_vendor_lead_time_days = Column(Float, default=0.0, comment='平均供应商交货时间(天)')
    
    sell_through_rate = Column(Float, default=0.0, comment='销售通过率')
    unfilled_customer_ordered_units = Column(Integer, default=0, comment='未完成的客户订单数量')
    
    # 可售库存
    sellable_on_hand_inventory_cost = Column(Float, default=0.0, comment='可售现有库存成本')
    sellable_on_hand_inventory_units = Column(Integer, default=0, comment='可售现有库存数量')
    
    # 不可售库存
    unsellable_on_hand_inventory_cost = Column(Float, default=0.0, comment='不可售现有库存成本')
    unsellable_on_hand_inventory_units = Column(Integer, default=0, comment='不可售现有库存数量')
    
    # 老化库存
    aged_90_plus_days_sellable_inventory_cost = Column(Float, default=0.0, comment='90天以上可售库存成本')
    aged_90_plus_days_sellable_inventory_units = Column(Integer, default=0, comment='90天以上可售库存数量')
    
    # 不良库存
    unhealthy_inventory_cost = Column(Float, default=0.0, comment='不良库存成本')
    unhealthy_inventory_units = Column(Integer, default=0, comment='不良库存数量')
    
    procurable_product_out_of_stock_rate = Column(Float, default=0.0, comment='可采购产品缺货率')
    uft = Column(Float, default=0.0, comment='UFT指标')
    receive_fill_rate = Column(Float, default=0.0, comment='收货填充率')
    
    currency_code = Column(String(10), default='USD', comment='货币代码')
    
    created_at = Column(DateTime, default=datetime.utcnow, comment='记录创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='记录更新时间')
    
    # 关系
    store = relationship('Store', back_populates='inventory_reports')
    
    # 索引
    __table_args__ = (
        Index('idx_store_date_range', 'store_id', 'report_start_date', 'report_end_date'),
    )
    
    def __repr__(self):
        return f"<InventoryReport(store='{self.store_id}', date='{self.report_start_date}')>"


class InventoryReportByASIN(Base):
    """库存报告表 - 按ASIN汇总"""
    __tablename__ = 'inventory_reports_by_asin'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(100), ForeignKey('stores.store_id'), nullable=False, index=True)
    report_start_date = Column(DateTime, nullable=False, index=True)
    report_end_date = Column(DateTime, nullable=False, index=True)
    
    asin = Column(String(20), nullable=False, index=True, comment='ASIN')
    
    # 库存指标（与汇总表相同字段）
    vendor_confirmation_rate = Column(Float, default=0.0)
    net_received_inventory_cost = Column(Float, default=0.0)
    net_received_inventory_units = Column(Integer, default=0)
    open_purchase_order_units = Column(Integer, default=0)
    average_vendor_lead_time_days = Column(Float, default=0.0)
    sell_through_rate = Column(Float, default=0.0)
    unfilled_customer_ordered_units = Column(Integer, default=0)
    sellable_on_hand_inventory_cost = Column(Float, default=0.0)
    sellable_on_hand_inventory_units = Column(Integer, default=0)
    unsellable_on_hand_inventory_cost = Column(Float, default=0.0)
    unsellable_on_hand_inventory_units = Column(Integer, default=0)
    aged_90_plus_days_sellable_inventory_cost = Column(Float, default=0.0)
    aged_90_plus_days_sellable_inventory_units = Column(Integer, default=0)
    unhealthy_inventory_cost = Column(Float, default=0.0)
    unhealthy_inventory_units = Column(Integer, default=0)
    procurable_product_out_of_stock_rate = Column(Float, default=0.0)
    uft = Column(Float, default=0.0)
    receive_fill_rate = Column(Float, default=0.0)
    
    currency_code = Column(String(10), default='USD')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index('idx_store_asin_date', 'store_id', 'asin', 'report_start_date'),
        Index('idx_asin', 'asin'),
    )
    
    def __repr__(self):
        return f"<InventoryReportByASIN(store='{self.store_id}', asin='{self.asin}')>"


class ReportRequest(Base):
    """报告请求记录表"""
    __tablename__ = 'report_requests'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_id = Column(String(100), ForeignKey('stores.store_id'), nullable=False, index=True)
    report_type = Column(String(100), nullable=False, index=True, comment='报告类型')
    report_id = Column(String(100), unique=True, index=True, comment='亚马逊报告ID')
    
    # 请求参数
    data_start_time = Column(DateTime, comment='数据开始时间')
    data_end_time = Column(DateTime, comment='数据结束时间')
    marketplace_ids = Column(JSON, comment='Marketplace ID列表')
    report_options = Column(JSON, comment='报告选项')
    
    # 状态
    status = Column(String(50), default='IN_QUEUE', index=True, comment='状态: IN_QUEUE/IN_PROGRESS/DONE/CANCELLED/FATAL')
    processing_status = Column(String(50), comment='处理状态')
    
    # 结果
    report_document_id = Column(String(100), comment='报告文档ID')
    document_url = Column(Text, comment='文档下载URL')
    compression_algorithm = Column(String(20), comment='压缩算法')
    
    # 时间戳
    requested_at = Column(DateTime, default=datetime.utcnow, comment='请求时间')
    processing_started_at = Column(DateTime, comment='开始处理时间')
    processing_ended_at = Column(DateTime, comment='处理完成时间')
    downloaded_at = Column(DateTime, comment='下载时间')
    parsed_at = Column(DateTime, comment='解析时间')
    
    # 错误信息
    error_message = Column(Text, comment='错误信息')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 索引
    __table_args__ = (
        Index('idx_store_type_status', 'store_id', 'report_type', 'status'),
        Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f"<ReportRequest(id='{self.report_id}', type='{self.report_type}', status='{self.status}')>"