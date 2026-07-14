"""
Custom exceptions for the ReLiOn Analysis Engine.
"""

class ReLiOnException(Exception):
    """Base exception for all ReLiOn Engine errors."""
    pass

class ValidationError(ReLiOnException):
    """Raised when input validation fails."""
    pass

class AnalysisError(ReLiOnException):
    """Raised when a mathematical operation fails (e.g. division by zero)."""
    pass

class DataQualityWarning(Warning):
    """Base class for warnings about data quality (e.g. SoH > 100%)."""
    pass
