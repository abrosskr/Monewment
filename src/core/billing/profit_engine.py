from enum import Enum
from decimal import Decimal
from typing import Dict, Optional
from pydantic import BaseModel, Field

class GpuType(str, Enum):
    RTX_3060 = "RTX_3060"
    RTX_3070 = "RTX_3070"
    RTX_3080 = "RTX_3080"
    RTX_3090 = "RTX_3090"
    RTX_4060 = "RTX_4060"
    RTX_4070 = "RTX_4070"
    RTX_4080 = "RTX_4080"
    RTX_4090 = "RTX_4090"
    A100_40GB = "A100_40GB"
    A100_80GB = "A100_80GB"
    H100 = "H100"

class GpuSpec(BaseModel):
    tflops: float
    tdp_watts: int
    octane_bench: int
    vram_gb: int

# Commercial Grade Hardware Database
HARDWARE_SPECS: Dict[GpuType, GpuSpec] = {
    GpuType.RTX_3060: GpuSpec(tflops=12.7, tdp_watts=170, octane_bench=180, vram_gb=12),
    GpuType.RTX_3070: GpuSpec(tflops=20.3, tdp_watts=220, octane_bench=290, vram_gb=8),
    GpuType.RTX_3080: GpuSpec(tflops=29.8, tdp_watts=320, octane_bench=420, vram_gb=10),
    GpuType.RTX_3090: GpuSpec(tflops=35.6, tdp_watts=350, octane_bench=640, vram_gb=24),
    GpuType.RTX_4060: GpuSpec(tflops=15.1, tdp_watts=115, octane_bench=270, vram_gb=8),
    GpuType.RTX_4070: GpuSpec(tflops=29.1, tdp_watts=200, octane_bench=510, vram_gb=12),
    GpuType.RTX_4080: GpuSpec(tflops=48.7, tdp_watts=320, octane_bench=930, vram_gb=16),
    GpuType.RTX_4090: GpuSpec(tflops=82.6, tdp_watts=450, octane_bench=1280, vram_gb=24),
    GpuType.A100_40GB: GpuSpec(tflops=19.5, tdp_watts=250, octane_bench=0, vram_gb=40), # Valid for DeepSync (AI), Octane lower priority
    GpuType.A100_80GB: GpuSpec(tflops=19.5, tdp_watts=300, octane_bench=0, vram_gb=80),
    GpuType.H100: GpuSpec(tflops=51.2, tdp_watts=700, octane_bench=0, vram_gb=80),
}

class ProfitCalculationRequest(BaseModel):
    gpu_type: GpuType
    electricity_cost_per_kwh: float = Field(..., gt=0, description="Cost of electricity in USD per kWh")
    active_hours_per_day: float = Field(24.0, ge=0, le=24, description="Number of hours the GPU is active per day")
    deep_sync_utilization: float = Field(0.5, ge=0, le=1.0, description="Fraction of time spent on DeepSync (AI Generation)")
    deep_render_utilization: float = Field(0.5, ge=0, le=1.0, description="Fraction of time spent on DeepRender (Rendering)")

class ProfitCalculationResponse(BaseModel):
    currency: str = "USD"
    daily_revenue: Decimal
    daily_electricity_cost: Decimal
    daily_profit: Decimal
    monthly_profit_projection: Decimal
    roi_days_estimate: Optional[int] = None # Requires hardware cost, optional for now

class ProfitEngine:
    # Base Rates (Commercial Placeholders - subject to adjustment)
    DEEP_SYNC_RATE_PER_TFLOPS_HOUR = Decimal("0.002") # e.g., 0.002 USD per TFLOPS-Hour
    DEEP_RENDER_RATE_PER_OCTANE_HOUR = Decimal("0.001") # e.g., 0.001 USD per OctaneBench-Hour

    @staticmethod
    def calculate_profit(request: ProfitCalculationRequest) -> ProfitCalculationResponse:
        spec = HARDWARE_SPECS[request.gpu_type]
        
        # 1. Calculate Revenue
        # DeepSync Revenue = TFLOPS * Rate * Hours * Utilization
        deepsync_daily_revenue = (
            Decimal(str(spec.tflops)) * 
            ProfitEngine.DEEP_SYNC_RATE_PER_TFLOPS_HOUR * 
            Decimal(str(request.active_hours_per_day)) * 
            Decimal(str(request.deep_sync_utilization))
        )
        
        # DeepRender Revenue = OctaneBench * Rate * Hours * Utilization
        deeprender_daily_revenue = (
            Decimal(str(spec.octane_bench)) * 
            ProfitEngine.DEEP_RENDER_RATE_PER_OCTANE_HOUR * 
            Decimal(str(request.active_hours_per_day)) * 
            Decimal(str(request.deep_render_utilization))
        )
        
        total_daily_revenue = deepsync_daily_revenue + deeprender_daily_revenue
        
        # 2. Calculate Cost (Electricity)
        # kWh = (Watts * Hours) / 1000
        daily_kwh = (spec.tdp_watts * request.active_hours_per_day) / 1000.0
        daily_electricity_cost = Decimal(str(daily_kwh)) * Decimal(str(request.electricity_cost_per_kwh))
        
        # 3. Calculate Profit
        daily_profit = total_daily_revenue - daily_electricity_cost
        
        return ProfitCalculationResponse(
            daily_revenue=round(total_daily_revenue, 4),
            daily_electricity_cost=round(daily_electricity_cost, 4),
            daily_profit=round(daily_profit, 4),
            monthly_profit_projection=round(daily_profit * 30, 4)
        )
