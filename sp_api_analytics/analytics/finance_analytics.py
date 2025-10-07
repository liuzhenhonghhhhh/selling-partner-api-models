"""
财务与利润分析模块
支持财务事件、收入、费用、利润分析
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from loguru import logger

from core.sp_client import SPAPIClient


class FinanceAnalytics:
    """财务数据分析器"""
    
    def __init__(self, client: SPAPIClient):
        self.client = client
        self.store_id = client.credentials.store_id
        self.store_name = client.credentials.store_name
    
    def list_financial_event_groups(
        self,
        started_after: Optional[str] = None,
        started_before: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取财务事件组列表
        
        Args:
            started_after: 开始时间之后
            started_before: 开始时间之前
            max_results: 最大结果数
        
        Returns:
            财务事件组列表
        """
        endpoint = "/finances/v0/financialEventGroups"
        
        params = {
            "MaxResultsPerPage": min(max_results, 100)
        }
        
        if started_after:
            params["FinancialEventGroupStartedAfter"] = started_after
        if started_before:
            params["FinancialEventGroupStartedBefore"] = started_before
        
        all_groups = []
        next_token = None
        
        logger.info(f"[{self.store_name}] 获取财务事件组...")
        
        while True:
            if next_token:
                params["NextToken"] = next_token
            
            try:
                response = self.client.get(endpoint, params=params)
                
                if "payload" in response and "FinancialEventGroupList" in response["payload"]:
                    groups = response["payload"]["FinancialEventGroupList"]
                    all_groups.extend(groups)
                    
                    if len(all_groups) >= max_results:
                        all_groups = all_groups[:max_results]
                        break
                    
                    next_token = response["payload"].get("NextToken")
                    if not next_token:
                        break
                else:
                    break
                    
            except Exception as e:
                logger.error(f"[{self.store_name}] 获取财务事件组失败: {e}")
                break
        
        logger.success(f"[{self.store_name}] 共获取 {len(all_groups)} 个财务事件组")
        return all_groups
    
    def list_financial_events(
        self,
        posted_after: Optional[str] = None,
        posted_before: Optional[str] = None,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        获取财务事件列表
        
        Args:
            posted_after: 发布时间之后
            posted_before: 发布时间之前
            max_results: 最大结果数
        
        Returns:
            财务事件数据
        """
        endpoint = "/finances/v0/financialEvents"
        
        params = {
            "MaxResultsPerPage": min(max_results, 100)
        }
        
        if posted_after:
            params["PostedAfter"] = posted_after
        if posted_before:
            params["PostedBefore"] = posted_before
        
        all_events = {
            "ShipmentEventList": [],
            "RefundEventList": [],
            "AdjustmentEventList": [],
            "ServiceFeeEventList": [],
            "RetrochargeEventList": [],
            "RentalTransactionEventList": [],
        }
        
        next_token = None
        
        logger.info(f"[{self.store_name}] 获取财务事件...")
        
        while True:
            if next_token:
                params["NextToken"] = next_token
            
            try:
                response = self.client.get(endpoint, params=params)
                
                if "payload" in response and "FinancialEvents" in response["payload"]:
                    events = response["payload"]["FinancialEvents"]
                    
                    # 合并各类事件
                    for event_type, event_list in all_events.items():
                        if event_type in events:
                            event_list.extend(events[event_type])
                    
                    next_token = response["payload"].get("NextToken")
                    if not next_token:
                        break
                else:
                    break
                    
            except Exception as e:
                logger.error(f"[{self.store_name}] 获取财务事件失败: {e}")
                break
        
        total_events = sum(len(events) for events in all_events.values())
        logger.success(f"[{self.store_name}] 共获取 {total_events} 个财务事件")
        
        return all_events
    
    def get_financial_events_by_order(self, order_id: str) -> Dict[str, Any]:
        """
        按订单ID获取财务事件
        
        Args:
            order_id: 订单ID
        
        Returns:
            财务事件数据
        """
        endpoint = f"/finances/v0/orders/{order_id}/financialEvents"
        
        try:
            response = self.client.get(endpoint)
            if "payload" in response and "FinancialEvents" in response["payload"]:
                return response["payload"]["FinancialEvents"]
        except Exception as e:
            logger.error(f"[{self.store_name}] 获取订单 {order_id} 财务事件失败: {e}")
        
        return {}
    
    def analyze_shipment_events(
        self,
        shipment_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分析发货事件（计算收入和费用）
        
        Args:
            shipment_events: 发货事件列表
        
        Returns:
            收入和费用分析
        """
        total_revenue = 0
        total_fees = 0
        total_refunds = 0
        
        revenue_breakdown = defaultdict(float)
        fee_breakdown = defaultdict(float)
        
        for event in shipment_events:
            # 处理订单项目
            for item in event.get("ShipmentItemList", []):
                # 收入项
                for charge in item.get("ItemChargeList", []):
                    amount = float(charge.get("ChargeAmount", {}).get("CurrencyAmount", 0))
                    charge_type = charge.get("ChargeType", "Unknown")
                    total_revenue += amount
                    revenue_breakdown[charge_type] += amount
                
                # 费用项
                for fee in item.get("ItemFeeList", []):
                    amount = float(fee.get("FeeAmount", {}).get("CurrencyAmount", 0))
                    fee_type = fee.get("FeeType", "Unknown")
                    total_fees += abs(amount)  # 费用通常是负数
                    fee_breakdown[fee_type] += abs(amount)
        
        net_profit = total_revenue - total_fees
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "total_revenue": round(total_revenue, 2),
            "total_fees": round(total_fees, 2),
            "net_profit": round(net_profit, 2),
            "profit_margin_percent": round(profit_margin, 2),
            "revenue_breakdown": {k: round(v, 2) for k, v in revenue_breakdown.items()},
            "fee_breakdown": {k: round(v, 2) for k, v in fee_breakdown.items()},
            "total_events": len(shipment_events),
            "analysis_time": datetime.now().isoformat(),
        }
    
    def get_profit_analysis(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        获取利润分析（最近N天）
        
        Args:
            days: 天数
        
        Returns:
            利润分析结果
        """
        # 计算时间范围
        posted_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        posted_before = datetime.utcnow().isoformat() + "Z"
        
        # 获取财务事件
        financial_events = self.list_financial_events(
            posted_after=posted_after,
            posted_before=posted_before
        )
        
        # 分析发货事件
        shipment_analysis = self.analyze_shipment_events(
            financial_events.get("ShipmentEventList", [])
        )
        
        # 分析退款
        refund_events = financial_events.get("RefundEventList", [])
        total_refunds = 0
        for event in refund_events:
            for item in event.get("ShipmentItemAdjustmentList", []):
                for charge in item.get("ItemChargeAdjustmentList", []):
                    amount = float(charge.get("ChargeAmount", {}).get("CurrencyAmount", 0))
                    total_refunds += abs(amount)
        
        # 调整后的净利润
        adjusted_profit = shipment_analysis["net_profit"] - total_refunds
        
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "period_days": days,
            "revenue": shipment_analysis["total_revenue"],
            "fees": shipment_analysis["total_fees"],
            "refunds": round(total_refunds, 2),
            "gross_profit": shipment_analysis["net_profit"],
            "net_profit": round(adjusted_profit, 2),
            "profit_margin": round((adjusted_profit / shipment_analysis["total_revenue"] * 100), 2) if shipment_analysis["total_revenue"] > 0 else 0,
            "revenue_breakdown": shipment_analysis["revenue_breakdown"],
            "fee_breakdown": shipment_analysis["fee_breakdown"],
            "refund_count": len(refund_events),
            "analysis_time": datetime.now().isoformat(),
        }
    
    def compare_profit_periods(
        self,
        current_days: int = 7,
        comparison_days: int = 7
    ) -> Dict[str, Any]:
        """
        对比两个周期的利润
        
        Args:
            current_days: 当前周期天数
            comparison_days: 对比周期天数
        
        Returns:
            利润对比分析
        """
        # 当前周期
        current_analysis = self.get_profit_analysis(days=current_days)
        
        # 对比周期
        comparison_end = datetime.utcnow() - timedelta(days=current_days)
        comparison_start = comparison_end - timedelta(days=comparison_days)
        
        financial_events = self.list_financial_events(
            posted_after=comparison_start.isoformat() + "Z",
            posted_before=comparison_end.isoformat() + "Z"
        )
        
        shipment_analysis = self.analyze_shipment_events(
            financial_events.get("ShipmentEventList", [])
        )
        
        # 计算变化
        def calc_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 2)
        
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "current_period": current_analysis,
            "comparison_period": {
                "revenue": shipment_analysis["total_revenue"],
                "fees": shipment_analysis["total_fees"],
                "net_profit": shipment_analysis["net_profit"],
            },
            "changes": {
                "revenue_change": calc_change(
                    current_analysis["revenue"],
                    shipment_analysis["total_revenue"]
                ),
                "profit_change": calc_change(
                    current_analysis["net_profit"],
                    shipment_analysis["net_profit"]
                ),
                "fee_change": calc_change(
                    current_analysis["fees"],
                    shipment_analysis["total_fees"]
                ),
            },
        }


class MultiStoreFinanceAnalytics:
    """多店铺财务分析器"""
    
    def __init__(self, clients: Dict[str, SPAPIClient]):
        self.clients = clients
        self.analyzers = {
            store_id: FinanceAnalytics(client)
            for store_id, client in clients.items()
        }
    
    def get_all_stores_profit_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        获取所有店铺的利润汇总
        
        Args:
            days: 天数
        
        Returns:
            所有店铺的利润汇总
        """
        all_profits = []
        
        for store_id, analyzer in self.analyzers.items():
            try:
                profit_analysis = analyzer.get_profit_analysis(days=days)
                all_profits.append(profit_analysis)
            except Exception as e:
                logger.error(f"获取店铺 {store_id} 利润数据失败: {e}")
        
        # 汇总数据
        total_revenue = sum(p["revenue"] for p in all_profits)
        total_fees = sum(p["fees"] for p in all_profits)
        total_refunds = sum(p["refunds"] for p in all_profits)
        total_profit = sum(p["net_profit"] for p in all_profits)
        
        return {
            "total_stores": len(all_profits),
            "total_revenue": round(total_revenue, 2),
            "total_fees": round(total_fees, 2),
            "total_refunds": round(total_refunds, 2),
            "total_profit": round(total_profit, 2),
            "average_profit_margin": round((total_profit / total_revenue * 100), 2) if total_revenue > 0 else 0,
            "store_profits": all_profits,
            "period_days": days,
            "analysis_time": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    print("财务分析模块已加载")