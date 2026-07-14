from pydantic import BaseModel
from .battery import ChemistryType

class ChemistryProfile(BaseModel):
    """Model defining chemistry-specific parameters for degradation and analysis."""
    chemistry_type: ChemistryType
    k: float  # Degradation coefficient per cycle
    threshold_capacity_ratio: float  # E.g. 0.8 for 80% EOL threshold
    typical_internal_resistance: float # Typical fresh cell IR in mOhm
    
# Hardcoded profiles based on literature averages
CHEMISTRY_PROFILES = {
    ChemistryType.LFP: ChemistryProfile(
        chemistry_type=ChemistryType.LFP,
        k=0.000035, # average of 0.00002-0.00005
        threshold_capacity_ratio=0.8,
        typical_internal_resistance=2.0
    ),
    ChemistryType.NMC: ChemistryProfile(
        chemistry_type=ChemistryType.NMC,
        k=0.000055, # average of 0.00003-0.00008
        threshold_capacity_ratio=0.75,
        typical_internal_resistance=3.0
    ),
    ChemistryType.NCA: ChemistryProfile(
        chemistry_type=ChemistryType.NCA,
        k=0.00007, # average of 0.00004-0.0001
        threshold_capacity_ratio=0.7,
        typical_internal_resistance=4.0
    )
}
