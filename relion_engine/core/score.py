from ..models.analysis import ScoreResult
from ..exceptions import AnalysisError

def calculate_general_score(tus: float, eus: float, alpha: float = 0.5, beta: float = 0.5) -> ScoreResult:
    """
    Calculate the general evaluation score combining technical and economic suitability.
    Score = alpha * TUS + beta * EUS
    """
    if abs((alpha + beta) - 1.0) > 0.001:
        raise AnalysisError("Alpha and beta must sum to 1.0")
        
    score = (alpha * tus) + (beta * eus)
    
    return ScoreResult(score=score)
