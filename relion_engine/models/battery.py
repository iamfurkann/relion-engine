from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Optional

class ChemistryType(str, Enum):
    LFP = "LFP"
    NMC = "NMC"
    NCA = "NCA"

class UsageScenario(str, Enum):
    """Target second-life usage scenario."""
    BESS = "BESS"           # Battery Energy Storage System (grid-scale)
    HOME = "HOME"           # Residential / home storage
    MICROGRID = "MICROGRID" # Micro-grid / off-grid

class BatteryInput(BaseModel):
    """Model for battery input data. Covers all 3 wizard steps from the report."""
    # Step 1: Battery Information
    chemistry_type: ChemistryType
    nominal_capacity: float = Field(..., gt=0, le=1000, description="Manufacturer nominal capacity in Ah")
    measured_capacity: float = Field(..., ge=0, description="Measured current capacity in Ah")
    cycle_count: int = Field(..., ge=0, le=50000, description="Number of full charge-discharge cycles")
    internal_resistance: float = Field(..., gt=0.001, le=10, description="Internal resistance in Ohm")
    age: Optional[float] = Field(None, ge=0, le=30, description="Battery age in years")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    
    # Step 2: Target Project
    usage_scenario: UsageScenario = Field(default=UsageScenario.BESS, description="Target second-life usage scenario")
    target_location: Optional[str] = Field(None, description="Target deployment location")
    expected_lifetime_years: float = Field(default=5.0, gt=0, le=30, description="Expected second-life service duration in years")

    @field_validator("measured_capacity")
    @classmethod
    def check_capacity_bounds(cls, v: float, info) -> float:
        """Allow measured capacity to be up to 110% of nominal."""
        if 'nominal_capacity' in info.data:
            nominal = info.data['nominal_capacity']
            if v > nominal * 1.1:
                raise ValueError(f"Measured capacity ({v}) cannot be more than 110% of nominal ({nominal})")
        return v
