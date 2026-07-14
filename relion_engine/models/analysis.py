from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class EconomicInput(BaseModel):
    """Model for economic analysis input data (Wizard Step 3)."""
    total_energy_kwh: float = Field(..., ge=0, description="Total expected energy delivery in kWh over project life")
    energy_price_per_kwh: float = Field(..., ge=0, description="Price of energy per kWh")
    total_cost: float = Field(..., ge=0, description="Total cost including testing, refurbishment, install (M_total)")
    investment_cost: float = Field(..., ge=0, description="Initial investment cost")
    project_lifetime_years: float = Field(default=5.0, gt=0, description="Project lifetime in years for payback calc")

class ResultWithWarnings(BaseModel):
    """Base class for results that might include warnings."""
    warnings: List[str] = Field(default_factory=list)

class SoHResult(ResultWithWarnings):
    soh: float = Field(..., ge=0, le=100)

class RULResult(ResultWithWarnings):
    rul: float = Field(..., ge=0)

class TUSResult(ResultWithWarnings):
    tus: float = Field(..., ge=0, le=100)

class EconomicResult(ResultWithWarnings):
    revenue: float
    net_gain: float
    roi: float
    payback_period_years: Optional[float] = None
    eus: float = Field(..., ge=0, le=100)

class ScoreResult(ResultWithWarnings):
    score: float = Field(..., ge=0, le=100)

class ChemistryInfo(BaseModel):
    """Chemistry profile info included in the result for display."""
    name: str
    k: float
    threshold_soh: float
    typical_resistance: float

class DegradationPoint(BaseModel):
    """Single point on the degradation curve."""
    cycle: int
    capacity: float
    soh_percent: float

class AnalysisResult(BaseModel):
    """Complete analysis result — the single object returned to the API/frontend."""
    # Core metrics
    soh: float
    rul: float
    tus: float
    net_gain: float
    revenue: float
    roi: float
    payback_period_years: Optional[float]
    eus: float
    general_score: float
    
    # Labels (Turkish)
    soh_label: str
    rul_label: str
    tus_label: str
    eus_label: str
    score_label: str
    score_color: str
    
    # Chart data
    degradation_curve: List[DegradationPoint]
    
    # Context
    chemistry_info: ChemistryInfo
    
    # System
    warnings: List[str]
