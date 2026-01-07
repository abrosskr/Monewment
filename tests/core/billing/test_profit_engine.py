import pytest
from decimal import Decimal
from src.core.billing.profit_engine import ProfitEngine, ProfitCalculationRequest, GpuType, GpuSpec

def test_profit_calculation_rtx_3060():
    # Scenario: RTX 3060, 0.10 USD/kWh, 24h active, 50/50 utilization
    request = ProfitCalculationRequest(
        gpu_type=GpuType.RTX_3060,
        electricity_cost_per_kwh=0.10,
        active_hours_per_day=24.0,
        deep_sync_utilization=0.5,
        deep_render_utilization=0.5
    )
    
    response = ProfitEngine.calculate_profit(request)
    
    # Validation
    # Specs: TFLOPS=12.7, TDP=170W, Octane=180
    
    # Revenue:
    # DeepSync: 12.7 * 0.002 * 24 * 0.5 = 0.3048
    # DeepRender: 180 * 0.001 * 24 * 0.5 = 2.16
    # Total Revenue = 2.4648
    assert response.daily_revenue == Decimal("2.4648")
    
    # Cost:
    # kWh = (170 * 24) / 1000 = 4.08
    # Cost = 4.08 * 0.10 = 0.408
    assert response.daily_electricity_cost == Decimal("0.4080")
    
    # Profit:
    # 2.4648 - 0.408 = 2.0568
    assert response.daily_profit == Decimal("2.0568")
    
    # Monthly:
    # 2.0568 * 30 = 61.704
    assert response.monthly_profit_projection == Decimal("61.7040")

def test_profit_calculation_rtx_4090():
    # Scenario: RTX 4090, 0.15 USD/kWh, 20h active
    request = ProfitCalculationRequest(
        gpu_type=GpuType.RTX_4090,
        electricity_cost_per_kwh=0.15,
        active_hours_per_day=20.0,
        deep_sync_utilization=0.8, # Mostly AI
        deep_render_utilization=0.2
    )
    
    response = ProfitEngine.calculate_profit(request)
    
    # Specs: TFLOPS=82.6, TDP=450W, Octane=1280
    
    # Revenue:
    # DeepSync: 82.6 * 0.002 * 20 * 0.8 = 2.6432
    # DeepRender: 1280 * 0.001 * 20 * 0.2 = 5.12
    # Total Revenue = 7.7632
    assert response.daily_revenue == Decimal("7.7632")
    
    # Cost:
    # kWh = (450 * 20) / 1000 = 9.0
    # Cost = 9.0 * 0.15 = 1.35
    assert response.daily_electricity_cost == Decimal("1.3500")
    
    # Profit:
    # 7.7632 - 1.35 = 6.4132
    assert response.daily_profit == Decimal("6.4132")
