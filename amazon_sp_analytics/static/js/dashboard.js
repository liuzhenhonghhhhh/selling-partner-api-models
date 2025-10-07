// 仪表板JavaScript
const API_BASE = '/api/v1';

let orderTrendChart = null;
let revenueTrendChart = null;

// 格式化货币
function formatCurrency(value) {
    return '$' + value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// 格式化数字
function formatNumber(value) {
    return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 加载实时数据
async function loadRealtimeData() {
    try {
        const response = await fetch(`${API_BASE}/realtime/overview?minutes=60`);
        const data = await response.json();
        
        document.getElementById('total-stores').textContent = data.total_stores;
        document.getElementById('total-orders-1h').textContent = formatNumber(data.total_orders_1h);
        document.getElementById('total-revenue-1h').textContent = formatCurrency(data.total_revenue_1h);
        document.getElementById('orders-per-hour').textContent = data.orders_per_hour.toFixed(2) + ' 单/小时';
        document.getElementById('revenue-per-hour').textContent = formatCurrency(data.revenue_per_hour) + '/小时';
        document.getElementById('average-order-value').textContent = formatCurrency(data.average_order_value);
        
        const now = new Date(data.timestamp);
        document.getElementById('last-update').textContent = '最后更新: ' + now.toLocaleString('zh-CN');
        
    } catch (error) {
        console.error('加载实时数据失败:', error);
    }
}

// 加载24小时数据
async function load24HourData() {
    try {
        const endDate = new Date();
        const startDate = new Date(endDate.getTime() - 24 * 60 * 60 * 1000);
        
        const response = await fetch(
            `${API_BASE}/sales/summary?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`
        );
        const data = await response.json();
        
        document.getElementById('orders-24h').textContent = formatNumber(data.total_orders);
        document.getElementById('revenue-24h').textContent = formatCurrency(data.total_sales);
        document.getElementById('units-24h').textContent = formatNumber(data.total_units);
        document.getElementById('units-per-order').textContent = data.average_units_per_order.toFixed(2);
        
    } catch (error) {
        console.error('加载24小时数据失败:', error);
    }
}

// 加载订单趋势
async function loadOrderTrend() {
    try {
        const endDate = new Date();
        const startDate = new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        const response = await fetch(
            `${API_BASE}/orders/trend?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}&granularity=day`
        );
        const data = await response.json();
        
        const labels = data.map(item => new Date(item.date).toLocaleDateString('zh-CN'));
        const orders = data.map(item => item.orders);
        
        const ctx = document.getElementById('orderTrendChart');
        
        if (orderTrendChart) {
            orderTrendChart.destroy();
        }
        
        orderTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '订单数',
                    data: orders,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('加载订单趋势失败:', error);
    }
}

// 加载销售额趋势
async function loadRevenueTrend() {
    try {
        const endDate = new Date();
        const startDate = new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000);
        
        const response = await fetch(
            `${API_BASE}/sales/trend?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}&granularity=day`
        );
        const data = await response.json();
        
        const labels = data.map(item => new Date(item.date).toLocaleDateString('zh-CN'));
        const sales = data.map(item => item.sales);
        
        const ctx = document.getElementById('revenueTrendChart');
        
        if (revenueTrendChart) {
            revenueTrendChart.destroy();
        }
        
        revenueTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '销售额',
                    data: sales,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
        
    } catch (error) {
        console.error('加载销售额趋势失败:', error);
    }
}

// 加载店铺排名
async function loadStoreRankings() {
    try {
        const endDate = new Date();
        const startDate = new Date(endDate.getTime() - 24 * 60 * 60 * 1000);
        
        const response = await fetch(
            `${API_BASE}/rankings/stores?metric=revenue&start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}&top_n=10`
        );
        const data = await response.json();
        
        const tbody = document.getElementById('store-rankings');
        tbody.innerHTML = '';
        
        data.forEach(store => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><span class="badge bg-primary">${store.rank}</span></td>
                <td>${store.store_name}</td>
                <td>${formatNumber(Math.round(store.value))}</td>
                <td>${formatCurrency(store.value)}</td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" role="progressbar" style="width: ${store.percentage}%"
                             aria-valuenow="${store.percentage}" aria-valuemin="0" aria-valuemax="100">
                            ${store.percentage.toFixed(1)}%
                        </div>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('加载店铺排名失败:', error);
    }
}

// 加载最近告警
async function loadRecentAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts?status=active&limit=5`);
        const data = await response.json();
        
        const container = document.getElementById('recent-alerts');
        container.innerHTML = '';
        
        if (data.length === 0) {
            container.innerHTML = '<div class="alert alert-success">暂无告警</div>';
            return;
        }
        
        data.forEach(alert => {
            const severityClass = alert.severity === 'critical' ? 'alert-danger' : 'alert-warning';
            const item = document.createElement('div');
            item.className = `list-group-item ${severityClass}`;
            item.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${alert.alert_type}</h6>
                    <small>${new Date(alert.alert_time).toLocaleString('zh-CN')}</small>
                </div>
                <p class="mb-1">${alert.message}</p>
            `;
            container.appendChild(item);
        });
        
    } catch (error) {
        console.error('加载告警失败:', error);
    }
}

// 初始化仪表板
function initDashboard() {
    loadRealtimeData();
    load24HourData();
    loadOrderTrend();
    loadRevenueTrend();
    loadStoreRankings();
    loadRecentAlerts();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
    
    // 每分钟自动刷新数据
    setInterval(() => {
        loadRealtimeData();
        load24HourData();
    }, 60000);
    
    // 每5分钟刷新图表和排名
    setInterval(() => {
        loadOrderTrend();
        loadRevenueTrend();
        loadStoreRankings();
        loadRecentAlerts();
    }, 300000);
});